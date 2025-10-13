import logging
from typing import Optional
import redis.asyncio as redis
import redis as redis_sync
from app.core.config import get_redis_url

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client = None
        self.sync_client = None
        self.is_connected = False
    
    async def connect(self, redis_url: str):
        # Don't create multiple connections if already connected
        if self.is_connected and self.client:
            return True
            
        try:
            # Create async client (optimized for Redis Cloud)
            self.client = redis.from_url(
                redis_url,
                # Connection pool configuration (optimized for Redis Cloud)
                max_connections=2,                # Very small pool for cloud Redis
                retry_on_timeout=True,             # Retry operations on timeout
                socket_keepalive=True,             # Enable TCP keepalive
                socket_keepalive_options={},       # TCP keepalive options
                socket_connect_timeout=5,          # Longer connection timeout for cloud
                socket_timeout=5,                  # Longer socket timeout for cloud
                health_check_interval=120,        # Less frequent health checks
                decode_responses=True,             # Automatically decode responses
                encoding='utf-8',                  # Default encoding
                retry_on_error=[redis.ConnectionError, redis.TimeoutError]  # Retry on these errors
            )
            await self.client.ping()
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
            self.is_connected = False
            return False
    
    def connect_sync(self, redis_url: str):
        """Connect to Redis synchronously (for Celery workers)"""
        # Don't create multiple connections if already connected
        if self.sync_client:
            return True
            
        try:
            # Create sync client (optimized for Redis Cloud)
            self.sync_client = redis_sync.from_url(
                redis_url,
                # Connection pool configuration (optimized for Redis Cloud)
                max_connections=2,                # Very small pool for cloud Redis
                retry_on_timeout=True,             # Retry operations on timeout
                socket_keepalive=True,             # Enable TCP keepalive
                socket_keepalive_options={},       # TCP keepalive options
                socket_connect_timeout=5,          # Longer connection timeout for cloud
                socket_timeout=5,                  # Longer socket timeout for cloud
                health_check_interval=120,        # Less frequent health checks
                decode_responses=True,             # Automatically decode responses
                encoding='utf-8',                  # Default encoding
                retry_on_error=[redis_sync.ConnectionError, redis_sync.TimeoutError]  # Retry on these errors
            )
            self.sync_client.ping()
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis (sync): {e}")
            self.sync_client = None
            return False
    
    async def close(self):
        if self.client:
            await self.client.close()
            self.is_connected = False
    
    def get_client(self):
        return self.client
    
    def get_sync_client(self):
        return self.sync_client
    
    async def ping(self) -> bool:
        try:
            if self.client:
                await self.client.ping()
                return True
            return False
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

redis_manager = RedisManager()
