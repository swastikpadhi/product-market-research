import asyncio
import logging
from app.worker.celery_app import celery_app
from app.services.research_workflow_orchestrator import research_workflow_orchestrator
from app.db.database_factory import database_factory, celery_context
from app.core.config import get_logger, settings

logger = get_logger(__name__)

# Initialize database connections for Celery worker
def initialize_worker_services():
    """Initialize database connections for Celery worker (sync)"""
    try:
        # Set context to Celery for sync operations
        database_factory.set_context(celery_context().context)
        
        # Initialize MongoDB (sync)
        mongodb_manager = database_factory.get_mongodb_manager()
        mongodb_manager.connect_sync(settings.mongodb_url)
        
        # Initialize PostgreSQL (sync)
        postgres_manager = database_factory.get_postgres_manager()
        postgres_manager.connect_sync(settings.postgres_url)
        
        # Initialize Redis (sync) - for Celery operations
        redis_manager = database_factory.get_redis_manager()
        redis_manager.connect_sync(settings.redis_url)
        
        logger.info("Worker services initialized successfully (sync)")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize worker services: {e}")
        return False

@celery_app.task(bind=True)
def process_research_task(self, request_id: str, product_idea: str,
                          research_depth: str):
    try:
        # Initialize worker services (sync)
        initialize_worker_services()
        
        self.update_state(
            state='STARTED',
            meta={
                'status': 'processing',
                'current_step': 'initializing',
                'progress': 0,
                'details': 'Starting research workflow...'
            }
        )
        
        # Execute research workflow using sync version
        result = research_workflow_orchestrator.execute_sync(
            request_id=request_id,
            product_idea=product_idea,
            research_depth=research_depth,
            celery_task=self
        )
        
        return {
            'status': 'completed',
            'result': result,
            'request_id': request_id
        }
        
    except Exception as e:
        logger.error(f"Research task {request_id} failed: {e}")
        # The research_workflow_orchestrator.execute() already handles credit deduction
        # in both success and failure cases, so we don't need to do it here
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'failed',
                'error': str(e),
                'request_id': request_id
            }
        )
        raise