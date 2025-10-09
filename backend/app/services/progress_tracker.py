import logging
from typing import Dict, Any, Set, Optional
from datetime import datetime
from app.services.task_repository import task_repository
from app.services.search_service import search_service
from app.db.redis_manager import redis_manager
from app.core.config import get_logger

logger = get_logger(__name__)

class ProgressTracker:
    ALL_CHECKPOINTS = {
        "initialization_complete",
        "queries_generated",
        "market_search_started",
        "market_search_completed", 
        "market_extraction_completed",
        "market_analysis_completed",
        "competitor_search_started",
        "competitor_search_completed",
        "competitor_extraction_completed", 
        "competitor_analysis_completed",
        "customer_search_started",
        "customer_search_completed",
        "customer_extraction_completed",
        "customer_analysis_completed",
        "report_generation_started",
        "report_generation_completed",
        "finalization_complete"
    }
    
    UI_STAGES = {
        (0, 10): "Initializing research workflow...",
        (10, 20): "Preparing research queries...",
        (20, 70): "Conducting market research...",
        (70, 90): "Generating research report...",
        (90, 100): "Finalizing research..."
    }
    
    def __init__(self):
        self.redis = redis_manager
    
    async def complete_checkpoint(self, request_id: str, checkpoint: str) -> bool:
            try:
                if checkpoint not in self.ALL_CHECKPOINTS:
                    logger.warning(f"Unknown checkpoint: {checkpoint}")
                    return False
                
                current_status = await self.get_status(request_id)
                completed_checkpoints = set()
                
                if current_status and 'completed_checkpoints' in current_status:
                    completed_checkpoints = set(current_status['completed_checkpoints'])
                
                completed_checkpoints.add(checkpoint)
                
                total_checkpoints = len(self.ALL_CHECKPOINTS)
                completed_count = len(completed_checkpoints)
                progress_percentage = int((completed_count / total_checkpoints) * 100)
                
                stage_description = self._get_stage_description(progress_percentage)
                
                status_data = {
                    "request_id": request_id,
                    "status": "processing",
                    "current_step": checkpoint,
                    "progress": progress_percentage,
                    "details": stage_description,
                    "completed_checkpoints": list(completed_checkpoints),
                    "total_checkpoints": total_checkpoints,
                    "last_updated": __import__('datetime').datetime.now().isoformat(),
                    "research_depth": current_status.get("research_depth", "standard") if current_status else "standard",
                    "product_idea": current_status.get("product_idea", "") if current_status else ""
                }
                
                # Use single status update method
                success = await self.update_status(request_id, status_data)
                
                if success:
                    logger.info(f"[{request_id}] Checkpoint {completed_count}/{total_checkpoints}: {checkpoint}")
                else:
                    logger.error(f"[{request_id}] Failed checkpoint: {checkpoint}")
                
                return success
                
            except Exception as e:
                logger.error(f"Failed to complete checkpoint {checkpoint} for {request_id}: {e}")
                return False
    
    def _get_stage_description(self, progress_percentage: int) -> str:
        for (min_progress, max_progress), description in self.UI_STAGES.items():
            if min_progress <= progress_percentage < max_progress:
                return description
        
        if progress_percentage >= 100:
            return "Research complete!"
        
        return "Research in progress..."
    
    async def update_status(self, request_id: str, status_data: Dict[str, Any], max_retries: int = 3) -> bool:
        """
        Update status in both MongoDB and Redis atomically.
        Single method that handles all status updates.
        """
        for attempt in range(max_retries):
            try:
                # Prepare update data for MongoDB
                update_data = {
                    "status": status_data.get("status", "processing"),
                    "current_step": status_data.get("current_step", "unknown"),
                    "progress": status_data.get("progress", 0),
                    "details": status_data.get("details", "Research in progress..."),
                    "completed_checkpoints": status_data.get("completed_checkpoints", []),
                    "total_checkpoints": status_data.get("total_checkpoints", 17),
                    "last_updated": status_data.get("last_updated", datetime.now().isoformat()),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Add completion timestamp if task is completed
                if status_data.get("status") in ["completed", "failed", "aborted"]:
                    update_data["completed_at"] = datetime.now().isoformat()
                
                # Step 1: Update MongoDB (source of truth)
                mongo_success = await task_repository.update(request_id, update_data)
                if not mongo_success:
                    logger.error(f"[{request_id}] MongoDB update failed on attempt {attempt + 1}")
                    continue
                
                # Step 2: Update Redis cache (fast access)
                redis_success = await self.set_status(request_id, status_data)
                if not redis_success:
                    logger.error(f"[{request_id}] Redis update failed on attempt {attempt + 1}")
                    continue
                
                # Both succeeded
                logger.debug(f"[{request_id}] Status update successful")
                return True
                
            except Exception as e:
                logger.error(f"[{request_id}] Status update failed on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"[{request_id}] All retry attempts failed")
                    return False
                
                # Wait before retry
                import asyncio
                await asyncio.sleep(0.1 * (attempt + 1))
        
        return False
    
    async def complete_task_atomic(
        self, 
        request_id: str, 
        final_status: str = "completed",
        result_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Atomically complete a task with final status and result data.
        This is the critical method that must succeed before task completion.
        """
        try:
            # Get current status to preserve some fields
            current_status = await self.get_status(request_id)
            
            # Prepare final status data
            final_status_data = {
                "request_id": request_id,
                "status": final_status,
                "current_step": "finalization_complete",
                "progress": 100,
                "details": "Research complete!" if final_status == "completed" else f"Research {final_status}",
                "completed_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "research_depth": current_status.get("research_depth", "standard") if current_status else "standard",
                "product_idea": current_status.get("product_idea", "") if current_status else "",
                "completed_checkpoints": current_status.get("completed_checkpoints", []) if current_status else [],
                "total_checkpoints": current_status.get("total_checkpoints", 17) if current_status else 17
            }
            
            # Use single status update method
            success = await self.update_status(request_id, final_status_data)
            
            if success and result_data:
                # If we have result data, update it separately after status is committed
                await task_repository.update(request_id, {"result": result_data})
                
                # Re-index task for search with updated data
                try:
                    updated_task = await task_repository.get_by_id(request_id)
                    if updated_task:
                        await search_service.index_task(updated_task)
                except Exception as e:
                    logger.warning(f"Failed to re-index completed task {request_id}: {e}")
            
            return success
            
        except Exception as e:
            logger.error(f"[{request_id}] Task completion failed: {e}")
            return False
    
    async def get_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status from Redis cache"""
        try:
            redis_client = self.redis.get_client()
            if not redis_client:
                return None
            
            cache_key = f"status:{request_id}"
            cached_data = redis_client.get(cache_key)
            
            if cached_data:
                import json
                return json.loads(cached_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting status from cache for {request_id}: {e}")
            return None
    
    async def set_status(self, request_id: str, status_data: Dict[str, Any]) -> bool:
        """Set status in Redis cache"""
        try:
            redis_client = self.redis.get_client()
            if not redis_client:
                return False
            
            cache_key = f"status:{request_id}"
            import json
            redis_client.setex(cache_key, 3600, json.dumps(status_data))
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting status in cache for {request_id}: {e}")
            return False
    
    async def invalidate_status(self, request_id: str) -> bool:
        """Invalidate status cache"""
        try:
            redis_client = self.redis.get_client()
            if not redis_client:
                return False
            
            cache_key = f"status:{request_id}"
            redis_client.delete(cache_key)
            
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating status cache for {request_id}: {e}")
            return False

progress_tracker = ProgressTracker()
