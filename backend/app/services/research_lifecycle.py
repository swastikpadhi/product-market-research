from typing import Dict, Any
from datetime import datetime

from app.core.langgraph import ResearchSupervisor
from app.services.task_repository import task_repository
from app.services.credit_service_manager import credit_service_manager
from app.services.progress_tracker import progress_tracker
from app.core.config import get_logger

logger = get_logger(__name__)

MAX_SOURCES = 20

class ResearchLifecycleManager:

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
            
            # Update progress tracker (MongoDB + Redis)
            try:
                status_data = {
                    'status': 'processing',
                    'current_step': step,
                    'progress': progress,
                    'details': details,
                    'last_updated': datetime.now().isoformat()
                }
                await progress_tracker.update_status(request_id, status_data)
                logger.debug(f"[{request_id}] Progress updated: {step} ({progress}%)")
            except Exception as e:
                logger.error(f"[{request_id}] Failed to update progress: {e}")
        
        return progress_callback
    
    async def execute(
        self,
        request_id: str,
        product_idea: str,
        research_depth: str,
        celery_task=None
    ):
        self._ensure_orchestrator_initialized()
        
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
            atomic_success = await progress_tracker.complete_task_atomic(
                request_id, 
                final_status, 
                result
            )
            
            if not atomic_success:
                logger.error(f"[{request_id}] Failed to atomically complete task - status may be inconsistent")
            
            await self._handle_credits_and_logging(request_id, result, research_depth)

        except Exception as e:
            logger.error(f"[{request_id}] Research workflow error: {e}", exc_info=True)
            
            # Use atomic status updater for failure as well
            error_result = {"success": False, "error": str(e)}
            atomic_success = await progress_tracker.complete_task_atomic(
                request_id, 
                "failed", 
                error_result
            )
            
            if not atomic_success:
                logger.error(f"[{request_id}] Failed to atomically mark task as failed - status may be inconsistent")
            
            # Still deduct credits for any API calls that succeeded before the failure
            await self._handle_credits_and_logging(request_id, error_result, research_depth)
            
            raise
    
    async def _handle_credits_and_logging(self, request_id: str, result: Dict[str, Any], research_depth: str):
        try:
            # Get task data to check completed checkpoints
            task_data = await task_repository.get_by_id(request_id)
            if not task_data:
                logger.error(f"[{request_id}] Task data not found for credit deduction")
                return
                
            user_id = task_data.get('user_id', 'default_user')
            completed_checkpoints = task_data.get('completed_checkpoints', [])
            
            # Calculate credits based on API usage (checkpoints completed)
            credits_to_deduct = self._calculate_credits_from_checkpoints(completed_checkpoints, research_depth)
            
            if credits_to_deduct > 0:
                credit_service = credit_service_manager.get_credit_service()
                deduction_result = await credit_service.deduct_credits(
                    user_id=user_id,
                    amount=credits_to_deduct,
                    research_request_id=request_id,
                    research_depth=research_depth
                )
                
                logger.info(
                    f"[{request_id}] Credits Deducted | "
                    f"Checkpoints: {len(completed_checkpoints)} | "
                    f"Amount: {credits_to_deduct} | "
                    f"Balance After: {deduction_result['balance_after']}"
                )
            else:
                logger.info(f"[{request_id}] No API calls made - no credits deducted")
                
        except Exception as e:
            logger.error(f"[{request_id}] Credit deduction error: {e}")
    
    def _calculate_credits_from_checkpoints(self, completed_checkpoints: list, research_depth: str) -> int:
        """Calculate credits based on actual API usage (checkpoints completed)"""
        if not completed_checkpoints:
            return 0
            
        # Count API-related checkpoints
        search_checkpoints = [cp for cp in completed_checkpoints if 'search' in cp]
        extract_checkpoints = [cp for cp in completed_checkpoints if 'extraction' in cp]
        
        # Calculate credits based on actual API usage
        # Each search checkpoint = 1 credit (basic) or 2 credits (advanced)
        # Each extract checkpoint = 1 credit per 5 URLs (basic) or 2 credits per 5 URLs (advanced)
        
        search_credits = 0
        extract_credits = 0
        
        # Search credits (3 agents × search calls)
        if search_checkpoints:
            # Basic research: 3 search calls × 1 credit = 3 credits
            # Standard/Comprehensive: 3 search calls × 2 credits = 6 credits
            search_credits = 3 if research_depth == "basic" else 6
            
        # Extract credits (based on research depth and URLs)
        if extract_checkpoints:
            # Basic: 3 agents × 5 URLs each = 15 URLs × 1/5 = 3 credits
            # Standard: 3 agents × 5 URLs each = 15 URLs × 2/5 = 6 credits  
            # Comprehensive: 3 agents × 10 URLs each = 30 URLs × 2/5 = 12 credits
            if research_depth == "basic":
                extract_credits = 3  # 15 URLs × 1/5
            elif research_depth == "standard":
                extract_credits = 6  # 15 URLs × 2/5
            else:  # comprehensive
                extract_credits = 12  # 30 URLs × 2/5
        
        total_credits = search_credits + extract_credits
        logger.info(f"Credit calculation: {len(search_checkpoints)} search + {len(extract_checkpoints)} extract = {total_credits} credits")
        
        return total_credits

research_lifecycle_manager = ResearchLifecycleManager()
