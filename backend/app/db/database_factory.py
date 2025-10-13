"""
Database Factory - Provides appropriate database connections based on context
"""
import logging
from typing import Optional, Union
from enum import Enum
from app.db.postgres_manager import postgres_manager
from app.db.mongodb_manager import mongodb_manager
from app.db.redis_manager import redis_manager
from app.core.config import get_logger

logger = get_logger(__name__)

class DatabaseContext(Enum):
    """Context for database operations"""
    FASTAPI = "fastapi"  # Async operations for FastAPI
    CELERY = "celery"    # Sync operations for Celery workers

class DatabaseFactory:
    """Factory for providing appropriate database connections based on context"""
    
    def __init__(self):
        self.context = DatabaseContext.FASTAPI  # Default to FastAPI context
    
    def set_context(self, context: DatabaseContext):
        """Set the current database context"""
        self.context = context
    
    def get_postgres_session(self):
        """Get PostgreSQL session based on context"""
        if self.context == DatabaseContext.FASTAPI:
            return postgres_manager.get_session()
        else:  # CELERY
            return postgres_manager.get_sync_session()
    
    def get_mongodb_collection(self, collection_name: str):
        """Get MongoDB collection based on context"""
        if self.context == DatabaseContext.FASTAPI:
            return mongodb_manager.get_collection(collection_name)
        else:  # CELERY
            return mongodb_manager.get_sync_collection(collection_name)
    
    def get_redis_client(self):
        """Get Redis client based on context"""
        if self.context == DatabaseContext.FASTAPI:
            return redis_manager.get_client()
        else:  # CELERY
            return redis_manager.get_sync_client()
    
    def get_postgres_manager(self):
        """Get PostgreSQL manager for direct access"""
        return postgres_manager
    
    def get_mongodb_manager(self):
        """Get MongoDB manager for direct access"""
        return mongodb_manager
    
    def get_redis_manager(self):
        """Get Redis manager for direct access"""
        return redis_manager

# Global database factory instance
database_factory = DatabaseFactory()

# Context managers for easy context switching
class DatabaseContextManager:
    """Context manager for database operations"""
    
    def __init__(self, context: DatabaseContext):
        self.context = context
        self.previous_context = None
    
    def __enter__(self):
        self.previous_context = database_factory.context
        database_factory.set_context(self.context)
        return database_factory
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_context:
            database_factory.set_context(self.previous_context)

# Convenience functions
def fastapi_context():
    """Context manager for FastAPI operations"""
    return DatabaseContextManager(DatabaseContext.FASTAPI)

def celery_context():
    """Context manager for Celery operations"""
    return DatabaseContextManager(DatabaseContext.CELERY)
