#!/usr/bin/env python3
"""
Clear Redis cache for balance and searches remaining
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clear_redis_cache():
    """Clear Redis cache for balance and searches remaining"""
    logger.info("🧹 Clearing Redis cache...")
    
    try:
        from app.db.database_factory import celery_context
        from app.db.redis_manager import redis_manager
        from app.core.config import settings
        
        with celery_context():
            # Connect to Redis
            redis_manager.connect_sync(settings.redis_url)
            
            if redis_manager.is_connected:
                logger.info("✅ Redis connected successfully")
                
                # Get Redis client
                redis_client = redis_manager.get_sync_client()
                
                if redis_client:
                    # First, let's see what keys exist
                    logger.info("🔍 Checking existing Redis keys...")
                    try:
                        all_keys = redis_client.keys("*")
                        logger.info(f"  Found {len(all_keys)} total keys in Redis")
                        
                        # Filter for relevant keys (focus on credit balance)
                        relevant_keys = []
                        for key in all_keys:
                            key_str = key.decode('utf-8') if isinstance(key, bytes) else str(key)
                            if any(term in key_str.lower() for term in ['credit', 'balance', 'global']):
                                relevant_keys.append(key_str)
                        
                        logger.info(f"  Found {len(relevant_keys)} relevant keys:")
                        for key in relevant_keys:
                            logger.info(f"    - {key}")
                        
                        # Clear all relevant keys
                        cleared_count = 0
                        for key in relevant_keys:
                            try:
                                redis_client.delete(key)
                                cleared_count += 1
                                logger.info(f"  ✅ Cleared: {key}")
                            except Exception as e:
                                logger.warning(f"  ⚠️  Failed to clear {key}: {e}")
                        
                        logger.info(f"🎉 Redis cache cleared! Cleared {cleared_count} relevant keys")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to check Redis keys: {e}")
                        return False
                    return True
                else:
                    logger.error("❌ Failed to get Redis client")
                    return False
            else:
                logger.error("❌ Failed to connect to Redis")
                return False
                
    except Exception as e:
        logger.error(f"❌ Failed to clear Redis cache: {e}")
        return False

def main():
    """Clear Redis cache"""
    logger.info("🚀 Starting Redis cache clearing...")
    
    success = clear_redis_cache()
    
    if success:
        logger.info("✅ Redis cache cleared successfully!")
        logger.info("💡 You can now run research tasks and the balance/searches should be fresh")
    else:
        logger.error("❌ Failed to clear Redis cache")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
