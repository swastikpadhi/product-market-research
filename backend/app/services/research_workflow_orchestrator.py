"""
Research Workflow Orchestrator - Orchestrates research workflow execution
"""
from typing import Dict, Any
from datetime import datetime
import asyncio

from app.core.langgraph import ResearchSupervisor
from app.repositories.task_repository import task_repository
from app.services.credit_service import credit_service
from app.services.progress_tracker import progress_tracker
from app.core.config import get_logger
from app.db.database_factory import celery_context

logger = get_logger(__name__)

MAX_SOURCES = 20

class ResearchWorkflowOrchestrator:

    def __init__(self):
        from app.core.config import settings
        self.openai_api_key = settings.openai_api_key
        self.tavily_api_key = settings.tavily_api_key
        self.orchestrator = None
    
    def _ensure_orchestrator_initialized(self):
        if self.orchestrator is None:
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            if not self.tavily_api_key:
                raise ValueError("TAVILY_API_KEY environment variable is required")
            
            self.orchestrator = ResearchSupervisor(
                self.openai_api_key,
                self.tavily_api_key
            )

    def _create_progress_callback(self, request_id: str, celery_task=None):
        async def progress_callback(step: str, progress: int, details: str):
            # Update Celery task state
            if celery_task:
                celery_task.update_state(
                    state='STARTED',
                    meta={
                        'status': 'processing',
                        'current_step': step,
                        'progress': progress,
                        'details': details
                    }
                )
            
            # Progress tracking is now handled by the checkpoint system
            # No need for separate status updates here
        
        return progress_callback
    
    async def execute(
        self,
        request_id: str,
        product_idea: str,
        research_depth: str,
        celery_task=None
    ):
        self._ensure_orchestrator_initialized()
        
        # Initialize progress tracker with complete status data
        progress_tracker.initialize_status(request_id, product_idea, research_depth)
        
        try:
            progress_callback = self._create_progress_callback(request_id, celery_task)
            
            result = await self.orchestrator.execute_research(
                product_idea=product_idea,
                sector="",
                research_depth=research_depth or "essential",
                request_id=request_id,
                abort_check=None,
                progress_callback=progress_callback
            )
            
            success = result.get("success", False)
            
            # Use atomic status updater to ensure both MongoDB and Redis are updated
            final_status = "completed" if success else "failed"
            atomic_success = progress_tracker.complete_task_atomic(
                request_id, 
                final_status, 
                result
            )
            
            if not atomic_success:
                logger.error(f"[{request_id}] Failed to atomically complete task - status may be inconsistent")
            
            await self._handle_credits_and_logging(request_id, result, research_depth)
            
            return result

        except Exception as e:
            logger.error(f"[{request_id}] Research workflow error: {e}", exc_info=True)
            
            # Use atomic status updater for failure as well
            error_result = {"success": False, "error": str(e)}
            atomic_success = progress_tracker.complete_task_atomic(
                request_id, 
                "failed", 
                error_result
            )
            
            if not atomic_success:
                logger.error(f"[{request_id}] Failed to atomically mark task as failed - status may be inconsistent")
            
            # Still deduct credits for any API calls that succeeded before the failure
            await self._handle_credits_and_logging(request_id, error_result, research_depth)
            
            return error_result
    
    async def _handle_credits_and_logging(self, request_id: str, result: Dict[str, Any], research_depth: str):
        try:
            # Get task data to check user_id
            task_data = await task_repository.get_by_id(request_id)
            if not task_data:
                logger.error(f"[{request_id}] Task data not found for credit deduction")
                return
                
            user_id = task_data.get('user_id', 'default_user')
            
            # Get completed checkpoints from Redis to verify task completed
            task_status = progress_tracker.get_task_status(request_id)
            completed_checkpoints_count = task_status.get('completed_checkpoints', 0) if task_status else 0
            
            # Only deduct credits if task completed successfully (all checkpoints done)
            if completed_checkpoints_count >= 17:  # All checkpoints completed
                credits_to_deduct = self._get_credits_for_research_depth(research_depth)
            else:
                credits_to_deduct = 0
                logger.info(f"[{request_id}] Task not fully completed ({completed_checkpoints_count}/17 checkpoints), no credits deducted")
            
            if credits_to_deduct > 0:
                deduction_result = credit_service.deduct_credits_sync(
                    user_id=user_id,
                    amount=credits_to_deduct,
                    research_request_id=request_id,
                    research_depth=research_depth
                )
                
                if deduction_result.get("success", False):
                    logger.info(f"[{request_id}] Successfully deducted {credits_to_deduct} credits for {user_id}. New balance: {deduction_result.get('balance_after', 'unknown')}")
                else:
                    logger.error(f"[{request_id}] Failed to deduct credits: {deduction_result.get('error', 'Unknown error')}")
            else:
                logger.info(f"[{request_id}] No credits to deduct (completed_checkpoints: {completed_checkpoints_count})")
                
        except Exception as e:
            logger.error(f"[{request_id}] Credit deduction error: {e}")
    
    def _get_credits_for_research_depth(self, research_depth: str) -> int:
        """Get credit cost for research depth"""
        credit_costs = {
            "basic": 6,
            "standard": 12, 
            "comprehensive": 18
        }
        return credit_costs.get(research_depth, 6)
    
    def _handle_credits_and_logging_sync(self, request_id: str, result: Dict[str, Any], research_depth: str):
        """Handle credit deduction for sync version (Celery workers)"""
        try:
            # Get task data to check user_id
            task_data = task_repository.get_by_id_sync(request_id)
            if not task_data:
                logger.error(f"[{request_id}] Task data not found for credit deduction")
                return
                
            user_id = task_data.get('user_id', 'default_user')
            
            # Get completed checkpoints from Redis to verify task completed
            task_status = progress_tracker.get_task_status(request_id)
            completed_checkpoints_count = task_status.get('completed_checkpoints', 0) if task_status else 0
            
            # Only deduct credits if task completed successfully (all checkpoints done)
            if completed_checkpoints_count >= 17:  # All checkpoints completed
                credits_to_deduct = self._get_credits_for_research_depth(research_depth)
            else:
                credits_to_deduct = 0
                logger.info(f"[{request_id}] Task not fully completed ({completed_checkpoints_count}/17 checkpoints), no credits deducted")
            
            if credits_to_deduct > 0:
                deduction_result = credit_service.deduct_credits_sync(
                    user_id=user_id,
                    amount=credits_to_deduct,
                    research_request_id=request_id,
                    research_depth=research_depth
                )
                
                if deduction_result.get("success", False):
                    logger.info(f"[{request_id}] Successfully deducted {credits_to_deduct} credits for {user_id}. New balance: {deduction_result.get('balance_after', 'unknown')}")
                else:
                    logger.error(f"[{request_id}] Failed to deduct credits: {deduction_result.get('error', 'Unknown error')}")
            else:
                logger.info(f"[{request_id}] No credits to deduct (completed_checkpoints: {completed_checkpoints_count})")
                
        except Exception as e:
            logger.error(f"[{request_id}] Credit deduction error: {e}")
    
    # Sync versions for Celery workers
    def execute_sync(
        self,
        request_id: str,
        product_idea: str,
        research_depth: str,
        celery_task=None
    ):
        """Execute research workflow (sync version for Celery)"""
        try:
            # Use celery_context for all database operations
            with celery_context():
                # Initialize progress tracking
                progress_tracker.initialize_status(request_id, product_idea, research_depth)
                
                # Execute the workflow using the orchestrator (sync version)
                self._ensure_orchestrator_initialized()
                
                # Run the workflow using sync version
                result = self.orchestrator.execute_research_sync(
                    product_idea=product_idea,
                    sector="",
                    research_depth=research_depth or "essential",
                    request_id=request_id,
                    abort_check=None,
                    progress_callback=None
                )
                
                # Update task status
                if result.get("success") == True:
                    task_repository.update_sync(request_id, {
                        "status": "completed",
                        "completed_at": datetime.now().isoformat(),
                        "result": result
                    })
                    
                    # Handle credit deduction for successful completion
                    self._handle_credits_and_logging_sync(request_id, result, research_depth)
                else:
                    task_repository.update_sync(request_id, {
                        "status": "failed",
                        "completed_at": datetime.now().isoformat(),
                        "error": result.get("error", "Unknown error")
                    })
                
                return result
                
        except Exception as e:
            logger.error(f"Error in sync execute: {e}")
            return {"success": False, "error": str(e)}

research_workflow_orchestrator = ResearchWorkflowOrchestrator()
