"""
Research Service - Business logic for research operations
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.credit_service_manager import credit_service_manager
from app.services.task_repository import task_repository
from app.services.search_service import search_service
from app.worker.tasks import process_research_task
from app.core.config import get_logger

logger = get_logger(__name__)

class ResearchService:
    """Business logic for research operations"""
    
    def __init__(self):
        self.credit_costs = {
            "basic": 6,         # 3 search (basic) + 15 URLs extract (basic) = 6 credits
            "standard": 12,      # 3 search (advanced) + 15 URLs extract (advanced) = 12 credits
            "comprehensive": 18   # 3 search (advanced) + 30 URLs extract (advanced) = 18 credits
        }
    
    async def submit_research_request(
        self, 
        product_idea: str, 
        research_depth: str, 
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Submit a new research request with business logic validation"""
        try:
            # Validate research depth
            if research_depth not in self.credit_costs:
                raise ValueError(f"Invalid research depth: {research_depth}")
            
            credits_needed = self.credit_costs[research_depth]
            
            # Check and validate credits
            await self._validate_user_credits(user_id, credits_needed)
            
            # Generate request ID
            request_id = self._generate_request_id(product_idea)
            
            # Create task data
            task_data = {
                "request_id": request_id,
                "product_idea": product_idea,
                "research_depth": research_depth,
                "max_sources": 20,
                "status": "pending",
                "credits_required": credits_needed,
                "user_id": user_id,
                "started_at": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            # Save task to repository
            await task_repository.create(task_data)
            
            # Index task for search (async, don't wait for it)
            try:
                await search_service.index_task(task_data)
            except Exception as e:
                logger.warning(f"Failed to index task {request_id} for search: {e}")
            
            # Submit to Celery worker
            task = process_research_task.delay(
                request_id=request_id,
                product_idea=product_idea,
                research_depth=research_depth
            )
            
            return {
                "request_id": request_id,
                "status": "submitted",
                "message": "Research task submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error submitting research request: {e}")
            raise
    
    async def get_research_status(self, request_id: str) -> Dict[str, Any]:
        """Get research status with business logic"""
        try:
            task = await task_repository.get_by_id(request_id)
            if not task:
                raise ValueError("Research task not found")
            
            return {
                "request_id": request_id,
                "status": task.get("status", "unknown"),
                "current_step": task.get("current_step", "initializing"),
                "progress": task.get("progress", 0),
                "details": task.get("details", "Research in progress..."),
                "started_at": task.get("started_at"),
                "completed_at": task.get("completed_at"),
                "research_depth": task.get("research_depth", "standard"),
                "product_idea": task.get("product_idea", ""),
                "completed_checkpoints": task.get("completed_checkpoints", []),
                "total_checkpoints": task.get("total_checkpoints", 17),
                "last_updated": task.get("last_updated", task.get("updated_at", task.get("started_at")))
            }
            
        except Exception as e:
            logger.error(f"Error getting research status: {e}")
            raise
    
    async def get_research_result(self, request_id: str) -> Dict[str, Any]:
        """Get research result with business logic"""
        try:
            task = await task_repository.get_by_id(request_id)
            if not task:
                raise ValueError("Research task not found")
            
            if task.get("status") != "completed":
                raise ValueError("Research task not completed yet")
            
            result = task.get("result", {})
            if not result:
                raise ValueError("Research result not found")
            
            return {
                "request_id": request_id,
                "status": "completed",
                "result": result,
                "metadata": {
                    "research_depth": task.get("research_depth", "standard"),
                    "product_idea": task.get("product_idea", ""),
                    "completed_at": task.get("completed_at"),
                    "started_at": task.get("started_at")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting research result: {e}")
            raise
    
    async def get_user_searches_remaining(self, user_id: str = "default") -> Dict[str, Any]:
        """Get remaining searches count with business logic"""
        try:
            credit_service = credit_service_manager.get_credit_service()
            account = await credit_service.get_account(user_id)
            
            if not account:
                # Create account with initial credits if it doesn't exist
                await credit_service.create_account(user_id, initial_credits=100.0)
                account = await credit_service.get_account(user_id)
            
            # Calculate searches remaining for each research depth
            searches_remaining = {}
            for depth, cost in self.credit_costs.items():
                searches_remaining[depth] = int(account.current_balance / cost) if account else 0
            
            return {
                "searches_remaining": searches_remaining,
                "credit_balance": account.current_balance if account else 0,
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting searches remaining: {e}")
            raise
    
    async def _validate_user_credits(self, user_id: str, credits_needed: int) -> None:
        """Validate user has sufficient credits"""
        credit_service = credit_service_manager.get_credit_service()
        account = await credit_service.get_account(user_id)
        
        if not account:
            await credit_service.create_account(user_id, initial_credits=100)
            account = await credit_service.get_account(user_id)
        
        if account.current_balance < credits_needed:
            raise ValueError(f"Insufficient credits. Need {credits_needed} credits, have {account.current_balance}")
    
    def _generate_request_id(self, product_idea: str) -> str:
        """Generate unique request ID"""
        return f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(product_idea) % 10000}"

# Global service instance
research_service = ResearchService()
