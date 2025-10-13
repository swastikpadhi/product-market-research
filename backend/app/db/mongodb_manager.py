import logging
from typing import Optional
from pymongo import AsyncMongoClient, MongoClient
from app.core.config import get_mongodb_url, get_logger

logger = get_logger(__name__)

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.sync_client = None
        self.database = None
        self.sync_database = None
        self.is_connected = False
    
    async def connect(self, mongodb_url: str):
        try:
            self.client = AsyncMongoClient(
                mongodb_url,
                # Connection pool configuration (optimized for free tier)
                maxPoolSize=5,                     # Very low for free tier
                minPoolSize=1,                     # Minimal connections
                maxIdleTimeMS=10000,               # Close connections after 10 seconds of inactivity
                serverSelectionTimeoutMS=3000,     # Shorter timeout for free tier
                connectTimeoutMS=5000,             # Shorter connection timeout
                socketTimeoutMS=10000,             # Shorter socket timeout
                retryWrites=True,                  # Retry write operations on network errors
                retryReads=True,                   # Retry read operations on network errors
                heartbeatFrequencyMS=30000,         # Less frequent health checks
                maxConnecting=2                    # Very limited concurrent connections
            )
            self.database = self.client.get_default_database()
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.database = None
            self.is_connected = False
            return False
    
    def connect_sync(self, mongodb_url: str):
        """Connect to MongoDB synchronously (for Celery workers)"""
        try:
            self.sync_client = MongoClient(
                mongodb_url,
                # Connection pool configuration (optimized for free tier)
                maxPoolSize=5,                     # Very low for free tier
                minPoolSize=1,                     # Minimal connections
                maxIdleTimeMS=10000,               # Close connections after 10 seconds of inactivity
                serverSelectionTimeoutMS=3000,     # Shorter timeout for free tier
                connectTimeoutMS=5000,             # Shorter connection timeout
                socketTimeoutMS=10000,             # Shorter socket timeout
                retryWrites=True,                  # Retry write operations on network errors
                retryReads=True,                   # Retry read operations on network errors
                heartbeatFrequencyMS=30000,         # Less frequent health checks
                maxConnecting=2                    # Very limited concurrent connections
            )
            self.sync_database = self.sync_client.get_default_database()
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB (sync): {e}")
            self.sync_client = None
            self.sync_database = None
            return False
    
    async def close(self):
        if self.client:
            await self.client.close()
            self.is_connected = False
        if self.sync_client:
            self.sync_client.close()
    
    def get_collection(self, collection_name: str):
        if self.database is None:
            raise Exception("MongoDB not connected")
        return self.database[collection_name]
    
    def get_sync_collection(self, collection_name: str):
        if self.sync_database is None:
            raise Exception("MongoDB sync not connected")
        return self.sync_database[collection_name]
    
    async def ping(self) -> bool:
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
            return False
        except Exception as e:
            logger.error(f"MongoDB ping failed: {e}")
            return False

mongodb_manager = MongoDBManager()
