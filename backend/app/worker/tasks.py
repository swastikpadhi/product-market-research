import asyncio
import logging
from app.worker.celery_app import celery_app
from app.services.research_lifecycle import research_lifecycle_manager
from app.db.mongodb_manager import mongodb_manager
from app.db.postgres_manager import postgres_manager
from app.db.redis_manager import redis_manager
from app.core.config import get_logger, settings
# Credit service will be initialized in the worker

logger = get_logger(__name__)

# Initialize database connections for Celery worker
async def initialize_worker_services():
    """Initialize database connections for Celery worker"""
    try:
        # Initialize MongoDB (async)
        await mongodb_manager.connect(settings.mongodb_url)
        
        # Initialize PostgreSQL (async)
        await postgres_manager.connect(settings.postgres_url)
        
        # Initialize Redis (async)
        await redis_manager.connect(settings.redis_url)
        
        # Initialize credit service
        from app.services.credit_service_manager import credit_service_manager
        
        # Get credit service instance (will be created if not exists)
        credit_service = credit_service_manager.get_credit_service()
        
        logger.info("Worker services initialized successfully")
        logger.info(f"Credit service initialized: {credit_service is not None}")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize worker services: {e}")
        return False

@celery_app.task(bind=True)
def process_research_task(self, request_id: str, product_idea: str,
                          research_depth: str):
    # Create single event loop for the entire task
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Initialize worker services
        loop.run_until_complete(initialize_worker_services())
        
        self.update_state(
            state='STARTED',
            meta={
                'status': 'processing',
                'current_step': 'initializing',
                'progress': 0,
                'details': 'Starting research workflow...'
            }
        )
        
        # Execute research workflow
        result = loop.run_until_complete(
            research_lifecycle_manager.execute(
                request_id=request_id,
                product_idea=product_idea,
                research_depth=research_depth,
                celery_task=self
            )
        )
        
        return {
            'status': 'completed',
            'result': result,
            'request_id': request_id
        }
        
    except Exception as e:
        logger.error(f"Research task {request_id} failed: {e}")
        # The research_lifecycle_manager.execute() already handles credit deduction
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
    finally:
        loop.close()