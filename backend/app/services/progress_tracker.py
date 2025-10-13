"""
Progress Tracker - Tracks research workflow checkpoints (Sync version for Celery workers)
Uses Redis for all progress tracking to avoid async/sync conflicts
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from app.db.redis_manager import redis_manager
from app.core.config import get_logger
from app.core.constants import ALL_CHECKPOINTS, TOTAL_CHECKPOINTS

logger = get_logger(__name__)

class ProgressTracker:
    """Tracks progress through research workflow checkpoints (Sync version for Celery workers)"""
    
    ALL_CHECKPOINTS = ALL_CHECKPOINTS
    TOTAL_CHECKPOINTS = TOTAL_CHECKPOINTS
    
    def __init__(self):
        self.redis = redis_manager
    
    def complete_checkpoint(self, request_id: str, checkpoint: str) -> bool:
        """Complete a checkpoint and update progress (sync version using Redis only)"""
        try:
            if checkpoint not in self.ALL_CHECKPOINTS:
                logger.warning(f"Unknown checkpoint: {checkpoint}")
                return False
            
            redis_client = self.redis.get_sync_client()
            if not redis_client:
                logger.error(f"[{request_id}] Redis sync client not available")
                return False
            
            # Step 1: Add checkpoint to Redis set
            checkpoints_key = f"checkpoints:{request_id}"
            redis_client.sadd(checkpoints_key, checkpoint)
            redis_client.expire(checkpoints_key, 3600)  # 1 hour TTL
            
            # Step 2: Increment counter
            counter_key = f"checkpoint_count:{request_id}"
            completed_count = redis_client.incr(counter_key)
            redis_client.expire(counter_key, 3600)
            
            total_checkpoints = self.TOTAL_CHECKPOINTS
            logger.info(f"[{request_id}] Checkpoint {completed_count}/{total_checkpoints}: {checkpoint}")
            
            # Step 3: Update status with progress
            self._update_status_sync(request_id, {
                "completed_checkpoints": completed_count,
                "progress": int((completed_count / total_checkpoints) * 100),
                "current_step": "processing" if completed_count < total_checkpoints else "final_report_delivered",
                "last_updated": datetime.now().isoformat()
            })
            
            return True
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to complete checkpoint {checkpoint}: {e}")
            return False
    
    def _update_status_sync(self, request_id: str, status_data: Dict[str, Any]) -> bool:
        """Update status in Redis cache (sync version)"""
        try:
            redis_client = self.redis.get_sync_client()
            if not redis_client:
                return False
            
            cache_key = f"status:{request_id}"
            
            # Get existing status
            existing_status = redis_client.get(cache_key)
            if existing_status:
                existing_data = json.loads(existing_status)
                existing_data.update(status_data)
                status_data = existing_data
            
            # Update cache (shorter TTL for cloud Redis)
            redis_client.setex(cache_key, 300, json.dumps(status_data))  # 5 minutes
            return True
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to update status in cache: {e}")
            return False
    
    def initialize_status(self, request_id: str, product_idea: str, research_depth: str) -> bool:
        """Initialize status for a new task (sync version using Redis only)"""
        try:
            redis_client = self.redis.get_sync_client()
            if not redis_client:
                logger.error(f"[{request_id}] Redis sync client not available")
                return False
            
            # Initialize checkpoint tracking
            checkpoints_key = f"checkpoints:{request_id}"
            counter_key = f"checkpoint_count:{request_id}"
            
            # Clear any existing data
            redis_client.delete(checkpoints_key)
            redis_client.delete(counter_key)
            
            # Initialize status
            initial_status = {
                "status": "processing",
                "current_step": "initializing",
                "progress": 0,
                "completed_checkpoints": 0,
                "last_updated": datetime.now().isoformat()
            }
            
            cache_key = f"status:{request_id}"
            redis_client.setex(cache_key, 300, json.dumps(initial_status))  # 5 minutes
            
            logger.info(f"[{request_id}] Initialized progress tracking")
            return True
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to initialize status: {e}")
            return False
    
    def complete_task_atomic(self, request_id: str, status: str, result: Dict[str, Any] = None) -> bool:
        """Complete task atomically (sync version using Redis only)"""
        try:
            redis_client = self.redis.get_sync_client()
            if not redis_client:
                logger.error(f"[{request_id}] Redis sync client not available")
                return False
            
            # Get completed checkpoints from Redis
            checkpoints_key = f"checkpoints:{request_id}"
            completed_checkpoints = list(redis_client.smembers(checkpoints_key))
            completed_checkpoints = [cp.decode() if isinstance(cp, bytes) else cp for cp in completed_checkpoints]
            
            # Update final status in Redis
            final_status = {
                "status": status,
                "progress": 100,
                "current_step": "final_report_delivered",
                "completed_checkpoints": completed_checkpoints,
                "completed_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat()
            }
            
            if result:
                final_status["result"] = result
            
            cache_key = f"status:{request_id}"
            redis_client.setex(cache_key, 300, json.dumps(final_status))  # 5 minutes
            
            # Store final result separately for longer retention
            if result:
                result_key = f"result:{request_id}"
                redis_client.setex(result_key, 3600, json.dumps(result))  # 1 hour
            
            logger.info(f"[{request_id}] Task completed with status: {status}")
            return True
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to complete task atomically: {e}")
            return False
    
    def get_task_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get task status from Redis"""
        try:
            redis_client = self.redis.get_sync_client()
            if not redis_client:
                return None
            
            cache_key = f"status:{request_id}"
            status_data = redis_client.get(cache_key)
            
            if status_data:
                return json.loads(status_data)
            return None
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to get task status: {e}")
            return None
    
    def get_task_result(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get task result from Redis"""
        try:
            redis_client = self.redis.get_sync_client()
            if not redis_client:
                return None
            
            result_key = f"result:{request_id}"
            result_data = redis_client.get(result_key)
            
            if result_data:
                return json.loads(result_data)
            return None
            
        except Exception as e:
            logger.error(f"[{request_id}] Failed to get task result: {e}")
            return None

# Global sync progress tracker instance
progress_tracker = ProgressTracker()