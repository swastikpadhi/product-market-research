from celery import Celery
from celery.signals import worker_ready
from app.core.config import settings, get_logger

logger = get_logger(__name__)

# Convert async PostgreSQL URL to sync URL for Celery
def get_sync_postgres_url():
    """Convert async PostgreSQL URL to sync URL for Celery"""
    from app.db.postgres_manager import convert_async_to_sync_url
    return convert_async_to_sync_url(settings.postgres_url)

# Use centralized configuration for broker and results backend
celery_app = Celery(
    'research_worker',
    broker=settings.redis_url,  # Use Redis for broker
    backend=f"database+{get_sync_postgres_url()}",  # Use sync PostgreSQL for result backend
    include=['app.worker.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    # PostgreSQL result backend configuration
    result_expires=3600,  # Results expire after 1 hour
    result_persistent=True,  # Persist results to PostgreSQL
    # Logging configuration - disable Celery's stdout logging
    worker_log_file=settings.celery_log_file,
    worker_log_level='INFO',
    worker_hijack_root_logger=False,  # Don't hijack root logger
    worker_log_color=False,  # Disable colored output
)

@worker_ready.connect
def initialize_services(sender=None, **kwargs):
    """Initialize all services and database connections when Celery worker starts"""
    try:
        from app.db.database_factory import celery_context, database_factory
        from app.services.credit_service import credit_service
        
        logger.info("🚀 Initializing Celery worker services...")
        
        # Initialize all database connections in Celery context
        with celery_context():
            # Initialize PostgreSQL
            postgres_manager = database_factory.get_postgres_manager()
            postgres_manager.connect_sync(settings.postgres_url)  # Actually connect with URL
            if postgres_manager.is_connected:
                logger.info("✅ PostgreSQL connected")
            else:
                logger.error("❌ PostgreSQL connection failed")
                raise RuntimeError("PostgreSQL not connected")
            
            # Initialize MongoDB
            mongodb_manager = database_factory.get_mongodb_manager()
            mongodb_manager.connect_sync(settings.mongodb_url)  # Actually connect with URL
            if mongodb_manager.is_connected:
                logger.info("✅ MongoDB connected")
            else:
                logger.error("❌ MongoDB connection failed")
                raise RuntimeError("MongoDB not connected")
            
            # Initialize Redis
            redis_manager = database_factory.get_redis_manager()
            redis_manager.connect_sync(settings.redis_url)  # Actually connect with URL
            if redis_manager.is_connected:
                logger.info("✅ Redis connected")
            else:
                logger.error("❌ Redis connection failed")
                raise RuntimeError("Redis not connected")
            
            # Initialize credit service
            credit_service._ensure_initialized()
            logger.info("✅ Credit service initialized")
            
        logger.info("🎉 All Celery services initialized successfully!")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Celery services: {e}")
        raise  # Re-raise to prevent Celery from starting with broken services
