"""
Credit Service Manager - Singleton pattern for consistent credit service access
"""
import logging
from typing import Optional
from app.services.credit_service import CreditService
from app.db.postgres_manager import postgres_manager
from app.core.config import get_logger

logger = get_logger(__name__)

class CreditServiceManager:
    """Singleton manager for credit service instances"""
    
    _instance: Optional['CreditServiceManager'] = None
    _credit_service: Optional[CreditService] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_credit_service(self) -> CreditService:
        """Get or create credit service instance"""
        if self._credit_service is None:
            if not postgres_manager.is_connected:
                raise RuntimeError("PostgreSQL not connected - cannot initialize credit service")
            self._credit_service = CreditService(postgres_manager)
            logger.info("Credit service instance created")
        return self._credit_service
    
    def reset(self):
        """Reset the singleton (useful for testing)"""
        self._credit_service = None

# Global instance
credit_service_manager = CreditServiceManager()
