import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.database_factory import database_factory, fastapi_context, celery_context
from app.core.config import get_logger
import asyncio

logger = get_logger(__name__)

class TaskRepository:
    """Task repository - works in both async and sync contexts"""
    
    def __init__(self):
        # Use database factory instead of direct manager access
        self.database_factory = database_factory
    
    async def create(self, task_data: Dict[str, Any]) -> bool:
        try:
            with fastapi_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
                result = await collection.insert_one(task_data)
                return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False
    
    async def get_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        try:
            with fastapi_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
                task = await collection.find_one({"request_id": request_id, "deleted": {"$ne": True}})
                if task:
                    task["_id"] = str(task["_id"])
                return task
            
        except Exception as e:
            logger.error(f"Error getting task {request_id}: {e}")
            return None
    
    
    async def update(self, request_id: str, update_data: Dict[str, Any]) -> bool:
        try:
            with fastapi_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
            
            # Check if update_data contains MongoDB operators (like $push)
            if any(key.startswith('$') for key in update_data.keys()):
                # Use atomic operations
                result = await collection.update_one(
                    {"request_id": request_id},
                    update_data
                )
            else:
                # Use replacement update
                update_data["updated_at"] = datetime.now().isoformat()
                result = await collection.update_one(
                    {"request_id": request_id},
                    {"$set": update_data}
                )
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating task {request_id}: {e}")
            return False
    
    async def list_tasks(self, page: int = 1, page_size: int = 10,
                         status: Optional[str] = None) -> Dict[str, Any]:
        try:
            with fastapi_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
            
            # Always exclude deleted tasks
            query = {"deleted": {"$ne": True}}
            if status:
                query["status"] = status
            
            # Get total count for pagination
            total_count = await collection.count_documents(query)
            
            # Get paginated results
            cursor = collection.find(query).sort("started_at", -1).skip((page - 1) * page_size).limit(page_size)
            tasks = []
            
            async for task in cursor:
                task["_id"] = str(task["_id"])
                tasks.append(task)
            
            # Calculate total pages
            total_pages = (total_count + page_size - 1) // page_size if total_count > 0 else 1
            
            return {
                "tasks": tasks,
                "total": total_count,
                "total_pages": total_pages,
                "page": page,
                "page_size": page_size
            }
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            return {
                "tasks": [],
                "total": 0,
                "total_pages": 1,
                "page": page,
                "page_size": page_size
            }
    
    async def delete(self, request_id: str) -> bool:
        try:
            with fastapi_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
            result = await collection.delete_one({"request_id": request_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting task {request_id}: {e}")
            return False
    
    # Sync versions for Celery workers
    def create_sync(self, task_data: Dict[str, Any]) -> bool:
        """Create task (sync version for Celery)"""
        try:
            with celery_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
                result = collection.insert_one(task_data)
                return result.inserted_id is not None
        except Exception as e:
            logger.error(f"Error creating task (sync): {e}")
            return False
    
    def get_by_id_sync(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID (sync version for Celery)"""
        try:
            with celery_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
                task = collection.find_one({"request_id": request_id})
                if task:
                    task["_id"] = str(task["_id"])
                return task
        except Exception as e:
            logger.error(f"Error getting task (sync): {e}")
            return None
    
    def update_sync(self, request_id: str, update_data: Dict[str, Any]) -> bool:
        """Update task (sync version for Celery)"""
        try:
            with celery_context():
                collection = self.database_factory.get_mongodb_collection("tasks")
                result = collection.update_one(
                    {"request_id": request_id},
                    {"$set": update_data}
                )
                return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating task (sync): {e}")
            return False

task_repository = TaskRepository()
