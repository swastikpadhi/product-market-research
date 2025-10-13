"""
Credit Repository - Database operations for credit management
"""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.database_factory import database_factory, fastapi_context, celery_context
from app.models.postgres_models import CreditBalance, CreditTransaction
from app.core.config import get_logger
import uuid

logger = get_logger(__name__)

class CreditRepository:
    """Database operations for credit management"""
    
    def __init__(self, postgres_manager=None):
        # Keep backward compatibility but use database factory
        self.postgres_manager = postgres_manager
    
    async def get_account(self, user_id: str) -> Optional[CreditBalance]:
        """Get user's credit account for current month (async)"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            with fastapi_context():
                postgres_manager = database_factory.get_postgres_manager()
                async with postgres_manager.get_session() as session:
                    from sqlalchemy import select
                    result = await session.execute(
                        select(CreditBalance).filter(
                            CreditBalance.user_id == user_id,
                            CreditBalance.month_year == current_month
                        )
                    )
                    account = result.scalar_one_or_none()
                    return account
        except Exception as e:
            logger.error(f"Error getting credit account for {user_id}: {e}")
            return None
    
    
    async def create_account(self, user_id: str, initial_credits: int = 100) -> bool:
        """Create new credit account for user"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            with fastapi_context():
                postgres_manager = database_factory.get_postgres_manager()
                async with postgres_manager.get_session() as session:
                    account = CreditBalance(
                        user_id=user_id,
                        month_year=current_month,
                        current_balance=initial_credits,
                        monthly_limit=1000
                    )
                    session.add(account)
                    await session.commit()
                    return True
        except Exception as e:
            logger.error(f"Error creating credit account for {user_id}: {e}")
            return False
    
    async def deduct_credits(
        self, 
        user_id: str, 
        amount: int,
        research_request_id: str, 
        research_depth: str
    ) -> dict:
        """Deduct credits from user account"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            async with self.postgres_manager.get_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(CreditBalance).filter(
                        CreditBalance.user_id == user_id,
                        CreditBalance.month_year == current_month
                    )
                )
                account = result.scalar_one_or_none()
                
                if not account:
                    # Create account with initial credits if it doesn't exist
                    account = CreditBalance(
                        user_id=user_id,
                        month_year=current_month,
                        current_balance=100,
                        monthly_limit=1000
                    )
                    session.add(account)
                    await session.commit()
                
                if account.current_balance < amount:
                    return {
                        "success": False,
                        "error": "Insufficient credits",
                        "balance_after": account.current_balance
                    }
                
                # Update account
                account.current_balance -= amount
                account.total_used_this_month += amount
                account.total_researches_this_month += 1
                
                # Create transaction record
                transaction = CreditTransaction(
                    transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                    balance_id=account.id,
                    amount=amount,
                    balance_after=account.current_balance,
                    research_request_id=research_request_id,
                    research_depth=research_depth
                )
                session.add(transaction)
                await session.commit()
                
                # Invalidate global searches remaining cache when credits are deducted
                try:
                    with fastapi_context():
                        redis_client = database_factory.get_redis_client()
                        if redis_client:
                            # Clear global credit balance cache
                            await redis_client.delete("global_credit_balance")
                            logger.info(f"Invalidated global credit balance cache")
                except Exception as e:
                    logger.warning(f"Failed to invalidate cache: {e}")
                
                return {
                    "success": True,
                    "balance_after": account.current_balance,
                    "transaction_id": transaction.transaction_id
                }
            
        except Exception as e:
            logger.error(f"Error deducting credits for {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "balance_after": 0
            }
    
    async def add_credits(self, user_id: str, amount: int, description: str = "") -> dict:
        """Add credits to user account"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            async with self.postgres_manager.get_session() as session:
                from sqlalchemy import select
                result = await session.execute(
                    select(CreditBalance).filter(
                        CreditBalance.user_id == user_id,
                        CreditBalance.month_year == current_month
                    )
                )
                account = result.scalar_one_or_none()
                
                if not account:
                    account = CreditBalance(
                        user_id=user_id,
                        month_year=current_month,
                        current_balance=amount,
                        monthly_limit=1000
                    )
                    session.add(account)
                else:
                    account.current_balance += amount
                
                # Create transaction record
                transaction = CreditTransaction(
                    transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                    balance_id=account.id,
                    amount=amount,
                    balance_after=account.current_balance
                )
                session.add(transaction)
                await session.commit()
                
                return {
                    "success": True,
                    "balance_after": account.current_balance,
                    "transaction_id": transaction.transaction_id
                }
            
        except Exception as e:
            logger.error(f"Error adding credits for {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "balance_after": 0
            }

    # Sync versions for Celery workers
    def get_sync(self, user_id: str) -> Optional[CreditBalance]:
        """Get user's credit account (sync version for Celery)"""
        try:
            with celery_context():
                postgres_manager = database_factory.get_postgres_manager()
                with postgres_manager.get_sync_session() as session:
                    current_month = datetime.now().strftime("%Y-%m")
                    result = session.query(CreditBalance).filter(
                        CreditBalance.user_id == user_id,
                        CreditBalance.month_year == current_month
                    )
                    return result.first()
        except Exception as e:
            logger.error(f"Error getting account (sync): {e}")
            return None
    
    def create_sync(self, user_id: str, initial_credits: int = 100) -> bool:
        """Create new credit account for user (sync version for Celery)"""
        try:
            with celery_context():
                postgres_manager = database_factory.get_postgres_manager()
                with postgres_manager.get_sync_session() as session:
                    current_month = datetime.now().strftime("%Y-%m")
                    
                    # Check if account already exists
                    existing = session.query(CreditBalance).filter(
                        CreditBalance.user_id == user_id,
                        CreditBalance.month_year == current_month
                    ).first()
                    
                    if existing:
                        return True  # Account already exists
                    
                    # Create new account
                    account = CreditBalance(
                        user_id=user_id,
                        month_year=current_month,
                        current_balance=initial_credits,
                        monthly_limit=1000
                    )
                    session.add(account)
                    session.commit()
                    return True
        except Exception as e:
            logger.error(f"Error creating account (sync): {e}")
            return False
    
    def deduct_sync(self, user_id: str, amount: int, research_request_id: str, research_depth: str) -> dict:
        """Deduct credits from user account (sync version for Celery)"""
        try:
            with celery_context():
                postgres_manager = database_factory.get_postgres_manager()
                with postgres_manager.get_sync_session() as session:
                    current_month = datetime.now().strftime("%Y-%m")
                    
                    # Get or create account
                    account = session.query(CreditBalance).filter(
                        CreditBalance.user_id == user_id,
                        CreditBalance.month_year == current_month
                    ).first()
                    
                    if not account:
                        account = CreditBalance(
                            user_id=user_id,
                            month_year=current_month,
                            current_balance=100,  # Default starting balance
                            monthly_limit=1000
                        )
                        session.add(account)
                        session.flush()  # Get the ID
                    
                    # Check if sufficient balance
                    if account.current_balance < amount:
                        return {
                            "success": False,
                            "error": "Insufficient credits",
                            "current_balance": account.current_balance,
                            "requested": amount
                        }
                    
                    # Deduct credits
                    account.current_balance -= amount
                    
                    # Create transaction record
                    transaction = CreditTransaction(
                        transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                        balance_id=account.id,
                        amount=-amount,  # Negative for deduction
                        balance_after=account.current_balance,
                        research_request_id=research_request_id,
                        research_depth=research_depth
                    )
                    session.add(transaction)
                    session.commit()
                    
                    return {
                        "success": True,
                        "balance_after": account.current_balance,
                        "transaction_id": transaction.transaction_id
                    }
        except Exception as e:
            logger.error(f"Error deducting credits (sync): {e}")
            return {"success": False, "error": str(e)}
    
    def add_sync(self, user_id: str, amount: int, description: str = "") -> dict:
        """Add credits to user account (sync version for Celery)"""
        try:
            with celery_context():
                postgres_manager = database_factory.get_postgres_manager()
                with postgres_manager.get_sync_session() as session:
                    current_month = datetime.now().strftime("%Y-%m")
                    
                    # Get or create account
                    account = session.query(CreditBalance).filter(
                        CreditBalance.user_id == user_id,
                        CreditBalance.month_year == current_month
                    ).first()
                    
                    if not account:
                        account = CreditBalance(
                            user_id=user_id,
                            month_year=current_month,
                            current_balance=amount,
                            monthly_limit=1000
                        )
                        session.add(account)
                    else:
                        account.current_balance += amount
                    
                    # Create transaction record
                    transaction = CreditTransaction(
                        transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
                        balance_id=account.id,
                        amount=amount,
                        balance_after=account.current_balance
                    )
                    session.add(transaction)
                    session.commit()
                    
                    return {
                        "success": True,
                        "new_balance": account.current_balance,
                        "transaction_id": transaction.transaction_id
                    }
        except Exception as e:
            logger.error(f"Error adding credits (sync): {e}")
            return {"success": False, "error": str(e)}

credit_repository = CreditRepository()
