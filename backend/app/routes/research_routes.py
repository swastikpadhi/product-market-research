import logging
import httpx
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from app.services.research_service import research_service
from app.repositories.task_repository import task_repository
from app.core.constants import TOTAL_CHECKPOINTS
from app.core.config import settings
from app.db.redis_manager import redis_manager
from app.schemas.research_schemas import (
    ResearchRequest, ResearchResponse, ResearchStatus, ResearchResult,
    SearchesRemaining, TaskList, TaskReport, TaskAction, CreditAddition
)

logger = logging.getLogger(__name__)

research_router = APIRouter()

# hCaptcha constants
HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"

async def verify_hcaptcha(hcaptcha_response: str) -> bool:
    """Verify hCaptcha response with hCaptcha API"""
    if not settings.hcaptcha_secret:
        logger.error("hcaptcha_secret not found in configuration")
        return False
        
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                HCAPTCHA_VERIFY_URL,
                data={
                    "secret": settings.hcaptcha_secret,
                    "response": hcaptcha_response
                }
            )
            result = response.json()
            return result.get("success", False)
    except Exception as e:
        logger.error(f"hCaptcha verification failed: {e}")
        return False

@research_router.post("", response_model=ResearchResponse)
async def submit_market_research(
    request: ResearchRequest,
    user_id: str = "default"
) -> ResearchResponse:
    """Submit a new market research request"""
    try:
        # Verify hCaptcha if provided
        if request.hcaptcha_response:
            is_valid = await verify_hcaptcha(request.hcaptcha_response)
            if not is_valid:
                raise HTTPException(status_code=400, detail="Invalid captcha verification")
        
        result = await research_service.submit_research_request(
            product_idea=request.product_idea,
            research_depth=request.research_depth,
            user_id=user_id
        )
        return ResearchResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting research request: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit research request: {str(e)}")

@research_router.get("/result/{request_id}", response_model=ResearchResult)
async def get_research_result(request_id: str) -> ResearchResult:
    """Get research result"""
    try:
        result_data = await research_service.get_research_result(request_id)
        return ResearchResult(**result_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting research result: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get research result: {str(e)}")

@research_router.get("/{request_id}/status", response_model=ResearchStatus)
async def get_research_status(request_id: str) -> ResearchStatus:
    """Get research task status"""
    try:
        # Use Redis with proper connection management
        redis_client = redis_manager.get_client()
        if not redis_client:
            # Fallback to research service if Redis not available
            status_data = await research_service.get_research_status(request_id)
            return ResearchStatus(**status_data)
        
        # Get checkpoint counter from Redis
        counter_key = f"checkpoint_count:{request_id}"
        completed_count = await redis_client.get(counter_key)
        completed_count = int(completed_count) if completed_count else 0
        
        # Get task data from MongoDB
        task_data = await task_repository.get_by_id(request_id)
        if not task_data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        total_checkpoints = TOTAL_CHECKPOINTS
        progress_percentage = int((completed_count / total_checkpoints) * 100)
        
        # Determine current step based on progress
        if completed_count == 0:
            current_step = "initializing"
        elif completed_count < total_checkpoints:
            current_step = "processing"
        else:
            current_step = "final_report_delivered"
        
        # Build status response - only what frontend needs
        status_data = {
            "request_id": request_id,
            "status": "completed" if completed_count >= total_checkpoints else "processing",
            "current_step": current_step,
            "progress": progress_percentage,
            "started_at": task_data.get("started_at"),
            "completed_at": task_data.get("completed_at"),
            "research_depth": task_data.get("research_depth", "basic"),
            "product_idea": task_data.get("product_idea", ""),
            "completed_checkpoints": completed_count
        }
        
        return ResearchStatus(**status_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting research status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get research status: {str(e)}")

@research_router.get("")
async def get_tasks(
    page: int = 1,
    page_size: int = 5,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Get all research tasks with pagination (frontend compatibility)."""
    try:
        result = await task_repository.list_tasks(
            page=page,
            page_size=page_size,
            status=status
        )
        
        return {
            "research_tasks": result["tasks"],
            "page": result["page"],
            "page_size": result["page_size"],
            "total": result["total"],
            "total_pages": result["total_pages"]
        }
        
    except Exception as e:
        logger.error(f"Error getting research tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get research tasks: {str(e)}")


@research_router.post("/{request_id}/rerun")
async def rerun_research_task(request_id: str) -> Dict[str, Any]:
    """Rerun a failed research task by deleting the old one and creating a new one."""
    try:
        # Get the original task data
        original_task = await task_repository.get_by_id(request_id)
        if not original_task:
            raise HTTPException(status_code=404, detail="Original task not found")
        
        # Only allow rerun for failed tasks
        if original_task.get("status") not in ["failed", "error"]:
            raise HTTPException(status_code=400, detail="Can only rerun failed tasks")
        
        # Extract original task parameters
        product_idea = original_task.get("product_idea", "")
        research_depth = original_task.get("research_depth", "standard")
        user_id = original_task.get("user_id", "default")
        
        if not product_idea:
            raise HTTPException(status_code=400, detail="Original task missing product idea")
        
        # Delete the old failed task
        await task_repository.delete(request_id)
        
        # Create a new task with the same parameters
        from app.services.research_service import research_service
        new_task = await research_service.submit_research_request(
            product_idea=product_idea,
            research_depth=research_depth,
            user_id=user_id
        )
        
        # Return the new task data with original parameters for frontend
        return {
            "request_id": new_task["request_id"],
            "status": new_task["status"],
            "message": new_task["message"],
            "product_idea": product_idea,
            "research_depth": research_depth,
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rerunning research task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to rerun research task: {str(e)}")

@research_router.get("/searches-remaining")
async def get_searches_remaining(user_id: str = "default") -> Dict[str, Any]:
    """Get remaining searches count using optimized global cache."""
    try:
        from app.services.research_service import research_service
        return await research_service.get_user_searches_remaining(user_id)
    except Exception as e:
        logger.error(f"Error getting searches remaining: {e}")
        raise HTTPException(status_code=500, detail="Failed to get searches remaining")

@research_router.get("/{request_id}/report")
async def get_task_report(request_id: str) -> Dict[str, Any]:
    """Get task report."""
    try:
        task = await task_repository.get_by_id(request_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        result = task.get('result', {})
        final_report = result.get('final_report', {})
        
        return {
            "request_id": request_id,
            "status": task.get('status', 'unknown'),
            "final_report": final_report
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task report: {e}")
        raise HTTPException(status_code=500, detail="Failed to get task report")

@research_router.delete("/{request_id}")
async def delete_task(request_id: str) -> Dict[str, Any]:
    """Delete a research task."""
    try:
        success = await task_repository.delete(request_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete task")

@research_router.post("/{request_id}/abort")
async def abort_task(request_id: str) -> Dict[str, Any]:
    """Abort a research task."""
    try:
        # Update task status to aborted
        success = await task_repository.update(request_id, {"status": "aborted"})
        if not success:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"message": "Task aborted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error aborting task: {e}")
        raise HTTPException(status_code=500, detail="Failed to abort task")

# REMOVED: /add-credits endpoint - Security vulnerability
# This endpoint allowed unlimited credit addition without authentication

@research_router.get("/search")
async def search_tasks(
    query: str,
    limit: int = 5,
    page: int = 1,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Search tasks using MongoDB text index on product_idea field - simple and fast"""
    try:
        if not query.strip():
            return {"results": [], "total": 0, "page": page, "total_pages": 0}
        
        # Direct MongoDB text search with pagination
        skip = (page - 1) * limit
        
        # Get collection
        collection = task_repository.database_factory.get_mongodb_collection("tasks")
        
        # Build search query with optional status filter
        search_filter = {
            "$text": {"$search": query},
            "deleted": {"$ne": True}
        }
        
        # Add status filter if provided
        if status and status != "all" and status != "":
            search_filter["status"] = status
        
        # MongoDB text search with pagination
        search_cursor = collection.find(search_filter).skip(skip).limit(limit)
        
        # Get total count for pagination
        total_results = await collection.count_documents(search_filter)
        
        # Execute search
        results = await search_cursor.to_list(length=limit)
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            if result.get("_id"):
                result["_id"] = str(result["_id"])
        
        # Calculate pagination
        total_pages = (total_results + limit - 1) // limit
        
        return {
            "results": results,
            "total": total_results,
            "page": page,
            "total_pages": total_pages,
            "limit": limit,
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Error searching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to search tasks")

@research_router.get("/search/suggestions")
async def get_search_suggestions(
    partial_query: str,
    limit: int = 5
) -> Dict[str, Any]:
    """Get search suggestions based on partial query using MongoDB text search on product_idea field"""
    try:
        if not partial_query.strip():
            return {"suggestions": []}
        
        # Get collection
        collection = task_repository.database_factory.get_mongodb_collection("tasks")
        
        # Simple text search for suggestions
        cursor = collection.find(
            {
                "$text": {"$search": partial_query},
                "deleted": {"$ne": True}
            }
        ).sort([("started_at", -1)]).limit(limit)
        
        results = await cursor.to_list(length=limit)
        
        # Format suggestions
        suggestions = []
        for result in results:
            suggestions.append({
                "query": result.get("product_idea", ""),
                "request_id": result.get("request_id"),
                "status": result.get("status"),
                "started_at": result.get("started_at")
            })
        
        return {
            "suggestions": suggestions,
            "query": partial_query
        }
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search suggestions")

router = research_router
