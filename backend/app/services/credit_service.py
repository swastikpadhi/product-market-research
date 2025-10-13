import logging
from typing import Dict, Any, Optional
from app.repositories.credit_repository import CreditRepository
from app.models.postgres_models import CreditBalance
from app.core.config import get_logger
from app.db.database_factory import database_factory, fastapi_context, celery_context
import asyncio

logger = get_logger(__name__)

class CreditService:
    """Business logic for credit management - works in both async and sync contexts"""
    
    _instance: Optional['CreditService'] = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Lazy initialization - don't initialize until first use
        self._initialized = False
        self.repository = None
    
    def _ensure_initialized(self):
        """Initialize the service if not already done"""
        if not self._initialized:
            # Use the current context instead of forcing fastapi_context
            postgres_manager = database_factory.get_postgres_manager()
            if not postgres_manager.is_connected:
                raise RuntimeError("PostgreSQL not connected - cannot initialize credit service")
            self.repository = CreditRepository(postgres_manager)
            self._initialized = True
    
    async def get_account(self, user_id: str) -> Optional[CreditBalance]:
        """Get user's credit account"""
        self._ensure_initialized()
        return await self.repository.get_account(user_id)
    
    async def create_account(self, user_id: str, initial_credits: int = 100) -> bool:
        """Create new credit account for user"""
        self._ensure_initialized()
        return await self.repository.create_account(user_id, initial_credits)
    
    # REMOVED: Async methods no longer needed
    # - deduct_credits() - unused after removing /add-credits endpoint
    # - add_credits() - unused after removing /add-credits endpoint
    
    # Sync versions for Celery workers
    def get_account_sync(self, user_id: str) -> Optional[CreditBalance]:
        """Get user's credit account (sync version for Celery)"""
        try:
            self._ensure_initialized()
            with celery_context():
                return self.repository.get_sync(user_id)
        except Exception as e:
            logger.error(f"Error in sync get_account: {e}")
            return None
    
    def create_account_sync(self, user_id: str, initial_credits: int = 100) -> bool:
        """Create new credit account for user (sync version for Celery)"""
        try:
            self._ensure_initialized()
            with celery_context():
                return self.repository.create_sync(user_id, initial_credits)
        except Exception as e:
            logger.error(f"Error in sync create_account: {e}")
            return False
    
    def deduct_credits_sync(self, user_id: str, amount: int,
                           research_request_id: str, research_depth: str) -> Dict[str, Any]:
        """Deduct credits from user account (sync version for Celery)"""
        try:
            self._ensure_initialized()
            with celery_context():
                result = self.repository.deduct_sync(user_id, amount, research_request_id, research_depth)
                
                # Invalidate cache after successful credit deduction
                if result.get("success", False):
                    from app.services.research_service import research_service
                    research_service._invalidate_credit_cache_sync(user_id)
                    logger.debug(f"Invalidated credit cache for {user_id} after sync deduction")
                
                return result
        except Exception as e:
            logger.error(f"Error in sync deduct_credits: {e}")
            return {"success": False, "error": str(e)}
    
    def add_credits_sync(self, user_id: str, amount: int, description: str = "") -> Dict[str, Any]:
        """Add credits to user account (sync version for Celery)"""
        try:
            self._ensure_initialized()
            with celery_context():
                result = self.repository.add_sync(user_id, amount, description)
                
                # Invalidate cache after successful credit addition
                if result.get("success", False):
                    from app.services.research_service import research_service
                    research_service._invalidate_credit_cache_sync(user_id)
                    logger.debug(f"Invalidated credit cache for {user_id} after sync credit addition")
                
                return result
        except Exception as e:
            logger.error(f"Error in sync add_credits: {e}")
            return {"success": False, "error": str(e)}
    
    @classmethod
    def reset(cls):
        """Reset the singleton (useful for testing)"""
        cls._instance = None

# Global instance
credit_service = CreditService()

