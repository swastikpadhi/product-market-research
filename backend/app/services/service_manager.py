"""
Service Manager - Centralized service initialization and management
"""
import logging
from typing import Dict, Any
from app.core.config import get_logger, settings
from app.db.postgres_manager import postgres_manager
from app.db.mongodb_manager import mongodb_manager
from app.db.redis_manager import redis_manager
from app.services.credit_service_manager import credit_service_manager

logger = get_logger(__name__)

class ServiceManager:
    """Centralized service initialization and management"""
    
    def __init__(self):
        self.services_initialized = False
        self.initialization_errors = []
    
    async def initialize_all_services(self) -> bool:
        """Initialize all required services"""
        try:
            # Validate API keys first
            self._validate_api_keys()
            
            # Initialize services in order
            await self._initialize_postgres()
            await self._initialize_credit_service()
            await self._initialize_mongodb()
            await self._initialize_redis()
            
            self.services_initialized = True
            logger.info("✅ All services initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            self.initialization_errors.append(str(e))
            return False
    
    def _validate_api_keys(self):
        """Validate required API keys are present"""
        if not settings.openai_api_key or not settings.tavily_api_key:
            raise ValueError("Missing required API keys: OPENAI_API_KEY and TAVILY_API_KEY")
    
    async def _initialize_postgres(self):
        """Initialize PostgreSQL database"""
        if not settings.postgres_database_url:
            raise ValueError("POSTGRES_DATABASE_URL is required")
        
        postgres_manager.connect(settings.postgres_database_url)
        if not postgres_manager.is_connected:
            raise RuntimeError("Failed to connect to PostgreSQL")
        
        logger.info("✅ PostgreSQL initialized successfully")
    
    async def _initialize_credit_service(self):
        """Initialize credit tracking service (requires PostgreSQL)"""
        if not postgres_manager.is_connected:
            raise RuntimeError("Cannot initialize credit service: PostgreSQL not available")
        
        # Initialize credit service manager
        credit_service = credit_service_manager.get_credit_service()
        logger.info("✅ Credit service initialized successfully")
    
    async def _initialize_mongodb(self):
        """Initialize MongoDB connection"""
        if not settings.mongodb_uri:
            raise ValueError("MONGODB_URI is required")
        
        success = await mongodb_manager.connect(settings.mongodb_uri)
        if not success:
            raise RuntimeError("Failed to connect to MongoDB")
        
        logger.info("✅ MongoDB initialized successfully")
    
    async def _initialize_redis(self):
        """Initialize Redis connection"""
        if not settings.redis_url:
            raise ValueError("REDIS_URL is required")
        
        await redis_manager.connect(settings.redis_url)
        if not redis_manager.is_connected:
            raise RuntimeError("Failed to connect to Redis")
        
        logger.info("✅ Redis initialized successfully")
    
    async def cleanup_services(self):
        """Cleanup all services on shutdown"""
        cleanup_errors = []
        
        try:
            postgres_manager.close()
            logger.info("PostgreSQL connection closed")
        except Exception as e:
            cleanup_errors.append(f"PostgreSQL cleanup error: {e}")
            logger.error(f"Error closing PostgreSQL: {e}")
        
        try:
            await mongodb_manager.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            cleanup_errors.append(f"MongoDB cleanup error: {e}")
            logger.error(f"Error closing MongoDB: {e}")
        
        try:
            await redis_manager.close()
            logger.info("Redis connection closed")
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
    
    async def _check_mongodb(self) -> str:
        """Check MongoDB connection"""
        try:
            if mongodb_manager.client:
                await mongodb_manager.client.admin.command('ping')
                return "healthy"
            return "not_connected"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def _check_postgresql(self) -> str:
        """Check PostgreSQL connection"""
        try:
            if postgres_manager.is_connected and postgres_manager.engine:
                return "healthy"
            return "not_connected"
        except Exception as e:
            return f"unhealthy: {str(e)}"
    
    def _check_redis(self) -> str:
        """Check Redis connection"""
        try:
            if redis_manager and redis_manager.is_connected:
                return "healthy"
            return "not_connected"
        except Exception as e:
            return f"error: {str(e)}"

# Global service manager instance
service_manager = ServiceManager()
