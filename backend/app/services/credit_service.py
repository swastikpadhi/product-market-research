import logging
from typing import Dict, Any, Optional
from app.repositories.credit_repository import CreditRepository
from app.models.postgres_models import CreditBalance
from app.core.config import get_logger

logger = get_logger(__name__)

class CreditService:
    """Business logic for credit management"""
    
    def __init__(self, postgres_manager):
        self.repository = CreditRepository(postgres_manager)
    
    async def get_account(self, user_id: str) -> Optional[CreditBalance]:
        """Get user's credit account"""
        return await self.repository.get_account(user_id)
    
    async def create_account(self, user_id: str, initial_credits: int = 100) -> bool:
        """Create new credit account for user"""
        return await self.repository.create_account(user_id, initial_credits)
    
    async def deduct_credits(self, user_id: str, amount: int,
                             research_request_id: str, research_depth: str) -> Dict[str, Any]:
        """Deduct credits from user account"""
        return await self.repository.deduct_credits(
            user_id, amount, research_request_id, research_depth
        )
    
    async def add_credits(self, user_id: str, amount: int, description: str = "") -> Dict[str, Any]:
        """Add credits to user account"""
        return await self.repository.add_credits(user_id, amount, description)

# Global credit service instance
credit_service = None
