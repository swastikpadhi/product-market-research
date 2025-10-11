from celery import Celery
from app.core.config import settings

# Convert async PostgreSQL URL to sync URL for Celery
def get_sync_postgres_url():
    """Convert async PostgreSQL URL to sync URL for Celery"""
    if settings.postgres_url.startswith('postgresql+asyncpg://'):
        # Convert async URL to sync URL
        sync_url = settings.postgres_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        # Convert ssl=require to sslmode=require for psycopg2 compatibility
        if 'ssl=require' in sync_url:
            sync_url = sync_url.replace('ssl=require', 'sslmode=require')
        
        return sync_url
    return settings.postgres_url

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
