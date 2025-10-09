"""
Credit Repository - Database operations for credit management
"""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.postgres_manager import postgres_manager
from app.models.postgres_models import CreditBalance, CreditTransaction
from app.core.config import get_logger
import uuid

logger = get_logger(__name__)

class CreditRepository:
    """Database operations for credit management"""
    
    def __init__(self, postgres_manager):
        self.postgres_manager = postgres_manager
    
    async def get_account(self, user_id: str) -> Optional[CreditBalance]:
        """Get user's credit account for current month"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            session = self.postgres_manager.get_session()
            account = session.query(CreditBalance).filter(
                CreditBalance.user_id == user_id,
                CreditBalance.month_year == current_month
            ).first()
            return account
        except Exception as e:
            logger.error(f"Error getting credit account for {user_id}: {e}")
            return None
        finally:
            session.close()
    
    async def create_account(self, user_id: str, initial_credits: int = 100) -> bool:
        """Create new credit account for user"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            session = self.postgres_manager.get_session()
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
            logger.error(f"Error creating credit account for {user_id}: {e}")
            return False
        finally:
            session.close()
    
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
            
            session = self.postgres_manager.get_session()
            account = session.query(CreditBalance).filter(
                CreditBalance.user_id == user_id,
                CreditBalance.month_year == current_month
            ).first()
            
            if not account:
                # Create account with initial credits if it doesn't exist
                account = CreditBalance(
                    user_id=user_id,
                    month_year=current_month,
                    current_balance=100,
                    monthly_limit=1000
                )
                session.add(account)
                session.commit()
            
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
            session.commit()
            
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
        finally:
            session.close()
    
    async def add_credits(self, user_id: str, amount: int, description: str = "") -> dict:
        """Add credits to user account"""
        try:
            current_month = datetime.now().strftime("%Y-%m")
            
            session = self.postgres_manager.get_session()
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
        finally:
            session.close()
