import os
import logging
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str = ""
    tavily_api_key: str = ""
    
    # Database URLs
    postgres_url: str = ""
    mongodb_url: str = ""
    redis_url: str = ""
    
    # API Configuration
    api_host: str = "0.0.0.0"
    port: int = 8000  # Using PORT to match your .env file
    
    # Celery Configuration
    celery_broker_url: str = ""
    celery_result_backend: str = ""
    
    # Logging Configuration
    log_file: str = ""
    celery_log_file: str = ""
    log_level: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"

# Create global settings instance
settings = Settings()

# Initialize Celery-specific URLs from main database URLs if not explicitly set
if not settings.celery_broker_url:
    settings.celery_broker_url = settings.redis_url
if not settings.celery_result_backend:
    # Use Redis for results backend (more reliable than PostgreSQL)
    settings.celery_result_backend = settings.redis_url

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        # Determine log file based on process type
        import sys
        if 'celery' in sys.argv or 'worker' in sys.argv:
            # Celery worker process
            log_file = settings.celery_log_file
        else:
            # Backend server process
            log_file = settings.log_file
        
        # Create file handler with process-specific log file
        if log_file and log_file.strip():
            # Ensure log file path is absolute or in a writable directory
            if not os.path.isabs(log_file):
                # If relative path, create logs directory and use absolute path
                if os.environ.get('ENVIRONMENT') == 'development':
                    # In development, use current working directory instead of /app
                    logs_dir = os.path.join(os.getcwd(), "logs")
                else:
                    # In production, use /app/logs
                    logs_dir = "/app/logs"
                os.makedirs(logs_dir, exist_ok=True)
                log_file = os.path.join(logs_dir, log_file)
            file_handler = logging.FileHandler(log_file)
        else:
            # Default to stdout if no log file specified
            file_handler = logging.StreamHandler()
        file_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Add formatter to file handler
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
        
        # Only add console handler for backend server (not Celery workers)
        if not (any('celery' in arg for arg in sys.argv) or any('worker' in arg for arg in sys.argv)):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    return logger

# Convenience functions for backward compatibility
def get_database_url() -> str:
    return settings.postgres_url

def get_mongodb_url() -> str:
    return settings.mongodb_url

def get_redis_url() -> str:
    return settings.redis_url

def get_openai_api_key() -> str:
    return settings.openai_api_key

def get_tavily_api_key() -> str:
    return settings.tavily_api_key
