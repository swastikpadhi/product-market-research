import logging
from typing import Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_database_url

def convert_async_to_sync_url(database_url: str) -> str:
    """Convert async PostgreSQL URL to sync URL for psycopg2 compatibility"""
    if not database_url.startswith('postgresql+asyncpg://'):
        return database_url
    
    # Convert async URL to sync URL
    sync_url = database_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    # Convert SSL parameters for psycopg2 compatibility
    if 'ssl=require' in sync_url:
        sync_url = sync_url.replace('ssl=require', 'sslmode=require')
    elif 'ssl=true' in sync_url:
        sync_url = sync_url.replace('ssl=true', 'sslmode=require')
    elif 'ssl=false' in sync_url:
        sync_url = sync_url.replace('ssl=false', 'sslmode=disable')
    
    # Handle other SSL variations
    if 'ssl=prefer' in sync_url:
        sync_url = sync_url.replace('ssl=prefer', 'sslmode=prefer')
    elif 'ssl=allow' in sync_url:
        sync_url = sync_url.replace('ssl=allow', 'sslmode=allow')
    
    return sync_url

logger = logging.getLogger(__name__)

class PostgreSQLManager:
    def __init__(self):
        self.engine = None
        self.sync_engine = None
        self.SessionLocal = None
        self.sync_SessionLocal = None
        self.is_connected = False
    
    async def connect(self, database_url: str):
        try:
            self.engine = create_async_engine(
                database_url,
                # Connection pool configuration (optimized for free tier)
                pool_size=2,                     # Minimal connections for free tier
                max_overflow=3,                  # Very limited additional connections
                pool_pre_ping=True,              # Validate connections before use
                pool_recycle=1800,               # Recycle connections every 30 minutes
                pool_timeout=10,                 # Shorter timeout for free tier
                echo=False                       # Set to True for SQL query logging
            )
            self.SessionLocal = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            self.is_connected = True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.engine = None
            self.SessionLocal = None
            self.is_connected = False
    
    def connect_sync(self, database_url: str):
        """Connect to PostgreSQL synchronously (for Celery workers)"""
        try:
            # Convert async URL to sync URL
            sync_url = convert_async_to_sync_url(database_url)
            
            self.sync_engine = create_engine(
                sync_url,
                # Connection pool configuration (optimized for free tier)
                pool_size=2,                     # Minimal connections for free tier
                max_overflow=3,                  # Very limited additional connections
                pool_pre_ping=True,              # Validate connections before use
                pool_recycle=1800,               # Recycle connections every 30 minutes
                pool_timeout=10,                 # Shorter timeout for free tier
                echo=False                       # Set to True for SQL query logging
            )
            self.sync_SessionLocal = sessionmaker(
                bind=self.sync_engine,
                expire_on_commit=False
            )
            self.is_connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL (sync): {e}")
            self.sync_engine = None
            self.sync_SessionLocal = None
            return False
    
    async def close(self):
        if self.engine:
            await self.engine.dispose()
            self.is_connected = False
        if self.sync_engine:
            self.sync_engine.dispose()
    
    def get_session(self):
        if not self.SessionLocal:
            raise Exception("PostgreSQL not connected")
        return self.SessionLocal()
    
    def get_sync_session(self):
        if not self.sync_SessionLocal:
            raise Exception("PostgreSQL sync not connected")
        return self.sync_SessionLocal()
    
    async def ping(self) -> bool:
        try:
            if self.engine:
                async with self.engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                return True
            return False
        except Exception as e:
            logger.error(f"PostgreSQL ping failed: {e}")
            return False

postgres_manager = PostgreSQLManager()
