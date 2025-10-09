import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException

from app.services.research_service import research_service
from app.services.task_repository import task_repository
from app.services.search_service import search_service
from app.services.progress_tracker import progress_tracker
from app.schemas.research_schemas import (
    ResearchRequest, ResearchResponse, ResearchStatus, ResearchResult,
    SearchesRemaining, TaskList, TaskReport, TaskAction, CreditAddition
)

logger = logging.getLogger(__name__)

research_router = APIRouter()

@research_router.post("/", response_model=ResearchResponse)
async def submit_market_research(
    request: ResearchRequest,
    user_id: str = "default"
) -> ResearchResponse:
    """Submit a new market research request"""
    try:
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

@research_router.get("/{request_id}/status", response_model=ResearchStatus)
async def get_research_status(request_id: str) -> ResearchStatus:
    """Get research task status"""
    try:
        # Always try cache first - this is the fast path
        cached_status = await progress_tracker.get_status(request_id)
        if cached_status:
            return ResearchStatus(**cached_status)
        
        # Fallback to service layer
        status_data = await research_service.get_research_status(request_id)
        
        # Cache the complete status data in Redis
        await progress_tracker.set_status(request_id, status_data)
        
        return ResearchStatus(**status_data)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting research status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get research status: {str(e)}")

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

@research_router.get("/")
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


@research_router.get("/searches-remaining")
async def get_searches_remaining(user_id: str = "default") -> Dict[str, Any]:
    """Get remaining searches count based on credit balance."""
    try:
        from app.services.credit_service import CreditService
        
        # Get credit service instance
        from app.services.credit_service_manager import credit_service_manager
        credit_service = credit_service_manager.get_credit_service()
        account = await credit_service.get_account(user_id)
        
        if not account:
            # Create account with initial credits if it doesn't exist
            await credit_service.create_account(user_id, initial_credits=100.0)
            account = await credit_service.get_account(user_id)
        
        # Calculate searches remaining based on actual API usage patterns
        # Basic: 3 search (basic) + 3 agents × 5 URLs each (basic) = 3 + 3 = 6 credits
        # Standard: 3 search (advanced) + 3 agents × 5 URLs each (advanced) = 6 + 6 = 12 credits  
        # Comprehensive: 3 search (advanced) + 3 agents × 10 URLs each (advanced) = 6 + 12 = 18 credits
        estimated_costs = {
            "basic": 6,         # 3 search (basic) + 15 URLs extract (basic) = 6 credits
            "standard": 12,     # 3 search (advanced) + 15 URLs extract (advanced) = 12 credits
            "comprehensive": 18  # 3 search (advanced) + 30 URLs extract (advanced) = 18 credits
        }
        
        searches_remaining = {}
        for depth, cost in estimated_costs.items():
            searches_remaining[depth] = int(account.current_balance / cost) if account else 0
        
        return {
            "searches_remaining": searches_remaining,
            "credit_balance": account.current_balance if account else 0,
            "user_id": user_id
        }
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

@research_router.post("/add-credits")
async def add_credits(
    amount: int = 100,
    user_id: str = "default"
) -> Dict[str, Any]:
    """Add credits to user account (for testing)."""
    try:
        from app.services.credit_service_manager import credit_service_manager
        
        credit_service = credit_service_manager.get_credit_service()
        result = await credit_service.add_credits(user_id, amount, "Test credits added")
        
        return {
            "success": result["success"],
            "message": f"Added {amount} credits",
            "balance_after": result["balance_after"]
        }
    except Exception as e:
        logger.error(f"Error adding credits: {e}")
        raise HTTPException(status_code=500, detail="Failed to add credits")

@research_router.get("/search")
async def search_tasks(
    query: str,
    limit: int = 10
) -> Dict[str, Any]:
    """Search tasks with Redis-powered suggestions and MongoDB data retrieval"""
    try:
        if not query.strip():
            return {"results": [], "suggestions": [], "total": 0}
        
        # Get search results from Redis
        search_results = await search_service.search_tasks(query, limit)
        
        # Get full task data from MongoDB for each result
        full_results = []
        for result in search_results:
            request_id = result.get("request_id")
            if request_id:
                full_task = await task_repository.get_by_id(request_id)
                if full_task:
                    # Combine Redis search metadata with MongoDB full data
                    full_task.update({
                        "relevance": result.get("relevance", 0),
                        "match_preview": result.get("match_preview", "")
                    })
                    full_results.append(full_task)
        
        return {
            "results": full_results,
            "total": len(full_results),
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
    """Get search suggestions based on partial query"""
    try:
        if not partial_query.strip():
            return {"suggestions": []}
        
        suggestions = await search_service.get_search_suggestions(partial_query, limit)
        
        return {
            "suggestions": suggestions,
            "query": partial_query
        }
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search suggestions")

router = research_router
