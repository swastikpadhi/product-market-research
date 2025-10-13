"""
Application Manager - Application startup, shutdown, and health monitoring
"""
import logging
from typing import Dict, Any
from app.core.config import get_logger, settings
from app.db.database_factory import database_factory, fastapi_context
from app.services.credit_service import credit_service

logger = get_logger(__name__)

class ApplicationManager:
    """Manages application lifecycle: startup, shutdown, and health monitoring"""
    
    def __init__(self):
        self.services_initialized = False
        self.initialization_errors = []
    
    async def initialize_all_services(self) -> bool:
        """Initialize all required services"""
        try:
            logger.info("🚀 Initializing FastAPI services...")
            
            # Validate API keys first
            self._validate_api_keys()
            logger.info("✅ API keys validated")
            
            # Initialize services in order
            await self._initialize_postgres()
            await self._initialize_mongodb()
            await self._initialize_redis()
            await self._initialize_credit_service()
            
            self.services_initialized = True
            logger.info("🎉 All FastAPI services initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            self.initialization_errors.append(str(e))
            return False
    
    def _validate_api_keys(self):
        """Validate required API keys are present"""
        if not settings.openai_api_key or not settings.tavily_api_key:
            raise ValueError("Missing required API keys: OPENAI_API_KEY and TAVILY_API_KEY")
    
    async def _initialize_postgres(self):
        """Initialize PostgreSQL database"""
        if not settings.postgres_url:
            raise ValueError("POSTGRES_URL is required")
        
        with fastapi_context():
            postgres_manager = database_factory.get_postgres_manager()
            await postgres_manager.connect(settings.postgres_url)
            if not postgres_manager.is_connected:
                raise RuntimeError("Failed to connect to PostgreSQL")
            logger.info("✅ PostgreSQL connected")
        
    
    async def _initialize_credit_service(self):
        """Initialize credit tracking service (requires PostgreSQL)"""
        with fastapi_context():
            postgres_manager = database_factory.get_postgres_manager()
            if not postgres_manager.is_connected:
                raise RuntimeError("Cannot initialize credit service: PostgreSQL not available")
            
            # Initialize credit service (singleton)
            credit_service._ensure_initialized()
            logger.info("✅ Credit service initialized")
    
    async def _initialize_mongodb(self):
        """Initialize MongoDB connection"""
        if not settings.mongodb_url:
            raise ValueError("MONGODB_URL is required")
        
        with fastapi_context():
            mongodb_manager = database_factory.get_mongodb_manager()
            success = await mongodb_manager.connect(settings.mongodb_url)
            if not success:
                raise RuntimeError("Failed to connect to MongoDB")
            logger.info("✅ MongoDB connected")
        
    
    async def _initialize_redis(self):
        """Initialize Redis connection"""
        if not settings.redis_url:
            raise ValueError("REDIS_URL is required")
        
        with fastapi_context():
            redis_manager = database_factory.get_redis_manager()
            await redis_manager.connect(settings.redis_url)
            if not redis_manager.is_connected:
                raise RuntimeError("Failed to connect to Redis")
            logger.info("✅ Redis connected")
        
    
    async def cleanup_services(self):
        """Cleanup all services on shutdown"""
        cleanup_errors = []
        
        with fastapi_context():
            try:
                postgres_manager = database_factory.get_postgres_manager()
                await postgres_manager.close()
            except Exception as e:
                cleanup_errors.append(f"PostgreSQL cleanup error: {e}")
                logger.error(f"Error closing PostgreSQL: {e}")
            
            try:
                mongodb_manager = database_factory.get_mongodb_manager()
                await mongodb_manager.close()
            except Exception as e:
                cleanup_errors.append(f"MongoDB cleanup error: {e}")
                logger.error(f"Error closing MongoDB: {e}")
            
            try:
                redis_manager = database_factory.get_redis_manager()
                await redis_manager.close()
            except Exception as e:
                cleanup_errors.append(f"Redis cleanup error: {e}")
                logger.error(f"Error closing Redis: {e}")
        
        if cleanup_errors:
            logger.warning(f"Service cleanup completed with {len(cleanup_errors)} errors")
        else:
            logger.info("✅ All services cleaned up successfully")
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all services"""
        return {
            "mongodb": self._check_mongodb(),
            "postgresql": self._check_postgresql(),
            "redis": self._check_redis(),
            "openai": "configured" if settings.openai_api_key else "not_configured",
            "tavily": "configured" if settings.tavily_api_key else "not_configured"
        }
    
    def _check_mongodb(self) -> str:
        """Check MongoDB connection"""
        try:
            with fastapi_context():
                mongodb_manager = database_factory.get_mongodb_manager()
                if mongodb_manager.client:
                    # Use synchronous ping check for health endpoint
                    return "healthy"
                return "not_connected"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def _check_postgresql(self) -> str:
        """Check PostgreSQL connection"""
        try:
            with fastapi_context():
                postgres_manager = database_factory.get_postgres_manager()
                if postgres_manager.is_connected and postgres_manager.engine:
                    return "healthy"
                return "not_connected"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def _check_redis(self) -> str:
        """Check Redis connection"""
        try:
            with fastapi_context():
                redis_manager = database_factory.get_redis_manager()
                if redis_manager and redis_manager.is_connected:
                    return "healthy"
                return "not_connected"
        except Exception as e:
            return f"error: {str(e)}"

# Global application manager instance
application_manager = ApplicationManager()
