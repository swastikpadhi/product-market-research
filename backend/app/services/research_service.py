"""
Research Service - Business logic for research operations
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from app.services.credit_service import credit_service
from app.repositories.task_repository import task_repository
from app.core.constants import TOTAL_CHECKPOINTS
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
        # Redis cache TTL - no instance-level caching
        self._cache_ttl = 15 * 60  # 15 minutes cache TTL
    
    # REMOVED: Async cache invalidation method no longer needed
    # - _invalidate_credit_cache() - unused after removing async credit methods
    def _invalidate_credit_cache_sync(self, user_id: str) -> None:
        """Invalidate Redis cached credit balance (sync version for Celery)"""
        try:
            from app.db.database_factory import database_factory, celery_context
            with celery_context():
                redis_manager = database_factory.get_redis_manager()
                if redis_manager.is_connected:
                    # Use sync Redis client for Celery context
                    redis_client = redis_manager.get_sync_client()
                    if redis_client:
                        redis_client.delete("global_credit_balance")
                        logger.debug(f"Cleared Redis credit balance cache (sync)")
        except Exception as e:
            logger.warning(f"Failed to clear Redis cache (sync): {e}")
    
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
                "created_at": datetime.now().isoformat(),
                "completed_checkpoints": []  # Initialize as empty array
            }
            
            # Save task to repository
            await task_repository.create(task_data)
            
            # Note: MongoDB text index will automatically index the task data
            # No need for separate indexing service
            
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
                "started_at": task.get("started_at"),
                "completed_at": task.get("completed_at"),
                "research_depth": task.get("research_depth", "standard"),
                "product_idea": task.get("product_idea", ""),
                "completed_checkpoints": len(task.get("completed_checkpoints", [])) if isinstance(task.get("completed_checkpoints"), list) else task.get("completed_checkpoints", 0)
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
        """Get remaining searches count using Redis cached credit balance with PostgreSQL fallback"""
        try:
            from app.db.database_factory import database_factory, fastapi_context
            import json
            
            with fastapi_context():
                redis_client = database_factory.get_redis_client()
                current_balance = None
                
                # Try Redis cache first for credit balance
                if redis_client:
                    try:
                        cached_balance = await redis_client.get("global_credit_balance")
                        if cached_balance:
                            current_balance = int(cached_balance)
                            logger.debug(f"Using Redis cached credit balance: {current_balance}")
                    except Exception as e:
                        logger.warning(f"Redis cache read failed: {e}")
                
                # Fallback to PostgreSQL if no cache
                if current_balance is None:
                    logger.debug(f"Fetching fresh credit balance from PostgreSQL")
                    try:
                        # Get account from PostgreSQL
                        account = await credit_service.get_account(user_id)
                        current_balance = account.current_balance if account else 0
                    except Exception as e:
                        logger.warning(f"PostgreSQL fallback failed: {e}")
                        current_balance = 0
                
                # Calculate searches remaining from credit balance
                searches_remaining = {
                    depth: int(current_balance / cost) 
                    for depth, cost in self.credit_costs.items()
                }
                
                result = {
                    "searches_remaining": searches_remaining,
                    "credit_balance": current_balance,
                    "user_id": user_id
                }
                
                # Cache only the credit balance in Redis for future requests
                if redis_client and current_balance is not None:
                    try:
                        await redis_client.setex("global_credit_balance", self._cache_ttl, str(current_balance))
                        logger.debug(f"Cached credit balance in Redis: {current_balance}")
                    except Exception as e:
                        logger.warning(f"Redis cache write failed: {e}")
                
                return result
                
        except Exception as e:
            logger.error(f"Error getting searches remaining: {e}")
            raise
    
    
    async def _validate_user_credits(self, user_id: str, credits_needed: int) -> None:
        """Validate user has sufficient credits using cached data from searches API"""
        try:
            # Get cached data from searches API (this will use cache if available)
            searches_data = await self.get_user_searches_remaining(user_id)
            current_balance = searches_data["credit_balance"]
            
            if current_balance < credits_needed:
                raise ValueError(f"Insufficient credits. Need {credits_needed} credits, have {current_balance}")
            
            logger.info(f"Credit validation passed for {user_id}: {current_balance} credits available")
            
        except ValueError:
            # Re-raise credit errors
            raise
        except Exception as e:
            # For other errors, log warning but proceed (graceful degradation)
            logger.warning(f"Credit validation failed for {user_id}, proceeding anyway: {e}")
            return
    
    def _generate_request_id(self, product_idea: str) -> str:
        """Generate unique request ID"""
        return f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(product_idea) % 10000}"

# Global service instance
research_service = ResearchService()
