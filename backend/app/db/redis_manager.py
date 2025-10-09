import logging
from typing import Optional
import redis
from app.core.config import get_redis_url

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    async def connect(self, redis_url: str):
        try:
            self.client = redis.from_url(
                redis_url,
                # Connection pool configuration (optimized for free tier)
                max_connections=5,                 # Very low for free tier
                retry_on_timeout=True,             # Retry operations on timeout
                socket_keepalive=True,             # Enable TCP keepalive
                socket_keepalive_options={},       # TCP keepalive options
                socket_connect_timeout=3,          # Shorter connection timeout
                socket_timeout=3,                  # Shorter socket timeout
                health_check_interval=60,          # Less frequent health checks
                decode_responses=True,             # Automatically decode responses
                encoding='utf-8',                  # Default encoding
                retry_on_error=[redis.ConnectionError, redis.TimeoutError]  # Retry on these errors
            )
            self.client.ping()
            self.is_connected = True
            logger.info("Connected to Redis with connection pool")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None
            self.is_connected = False
            return False
    
    async def close(self):
        if self.client:
            self.client.close()
            self.is_connected = False
            logger.info("Redis connection closed")
    
    def get_client(self):
        return self.client
    
    def ping(self) -> bool:
        try:
            if self.client:
                self.client.ping()
                return True
            return False
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

redis_manager = RedisManager()
