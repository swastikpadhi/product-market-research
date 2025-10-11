import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.db.mongodb_manager import mongodb_manager
from app.core.config import get_logger

logger = get_logger(__name__)

class TaskRepository:
    def __init__(self):
        self.db = mongodb_manager
    
    async def create(self, task_data: Dict[str, Any]) -> bool:
        try:
            collection = self.db.get_collection("tasks")
            result = await collection.insert_one(task_data)
            return result.inserted_id is not None
            
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return False
    
    async def get_by_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        try:
            collection = self.db.get_collection("tasks")
            task = await collection.find_one({"request_id": request_id, "deleted": {"$ne": True}})
            if task:
                task["_id"] = str(task["_id"])
            return task
            
        except Exception as e:
            logger.error(f"Error getting task {request_id}: {e}")
            return None
    
    async def update(self, request_id: str, update_data: Dict[str, Any]) -> bool:
        try:
            collection = self.db.get_collection("tasks")
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
            collection = self.db.get_collection("tasks")
            
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
            collection = self.db.get_collection("tasks")
            result = await collection.delete_one({"request_id": request_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting task {request_id}: {e}")
            return False

task_repository = TaskRepository()
