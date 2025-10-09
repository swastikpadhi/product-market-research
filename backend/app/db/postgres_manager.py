import logging
from typing import Optional
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import get_database_url

logger = logging.getLogger(__name__)

class PostgreSQLManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.is_connected = False
    
    def connect(self, database_url: str):
        try:
            self.engine = create_engine(
                database_url,
                # Connection pool configuration (optimized for free tier)
                pool_size=2,                     # Minimal connections for free tier
                max_overflow=3,                  # Very limited additional connections
                pool_pre_ping=True,              # Validate connections before use
                pool_recycle=1800,               # Recycle connections every 30 minutes
                pool_timeout=10,                 # Shorter timeout for free tier
                echo=False                       # Set to True for SQL query logging
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.is_connected = True
            logger.info("Connected to PostgreSQL with connection pool")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            self.engine = None
            self.SessionLocal = None
            self.is_connected = False
    
    def close(self):
        if self.engine:
            self.engine.dispose()
            self.is_connected = False
            logger.info("PostgreSQL connection closed")
    
    def get_session(self):
        if not self.SessionLocal:
            raise Exception("PostgreSQL not connected")
        return self.SessionLocal()
    
    def ping(self) -> bool:
        try:
            if self.engine:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                return True
            return False
        except Exception as e:
            logger.error(f"PostgreSQL ping failed: {e}")
            return False

postgres_manager = PostgreSQLManager()
