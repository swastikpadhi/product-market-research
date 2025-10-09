#!/usr/bin/env python3
"""
Script to index existing tasks in MongoDB to Redis for search functionality.
This should be run once to index all existing tasks.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.mongodb_manager import mongodb_manager
from app.db.redis_manager import redis_manager
from app.services.search_service import search_service
from app.core.config import settings, get_logger

logger = get_logger(__name__)

async def index_existing_tasks():
    """Index all existing tasks from MongoDB to Redis for search."""
    try:
        # Connect to databases
        print("Connecting to MongoDB...")
        await mongodb_manager.connect(settings.mongodb_uri)
        
        print("Connecting to Redis...")
        await redis_manager.connect(settings.redis_url)
        
        # Get all tasks from MongoDB
        print("Fetching tasks from MongoDB...")
        collection = mongodb_manager.get_collection("tasks")
        tasks = list(collection.find({}))
        
        print(f"Found {len(tasks)} tasks to index")
        
        indexed_count = 0
        for task in tasks:
            try:
                # Convert ObjectId to string for JSON serialization
                if '_id' in task:
                    task['_id'] = str(task['_id'])
                
                # Index the task
                success = await search_service.index_task(task)
                if success:
                    indexed_count += 1
                    print(f"✅ Indexed: {task.get('request_id', 'unknown')}")
                else:
                    print(f"❌ Failed to index: {task.get('request_id', 'unknown')}")
                    
            except Exception as e:
                print(f"❌ Error indexing task {task.get('request_id', 'unknown')}: {e}")
        
        print(f"\n🎉 Indexing complete! {indexed_count}/{len(tasks)} tasks indexed successfully")
        
        # Test search functionality
        print("\nTesting search functionality...")
        test_results = await search_service.search_tasks("crypto", limit=5)
        print(f"Search test results: {len(test_results)} results found")
        
        # Test suggestions
        test_suggestions = await search_service.get_search_suggestions("crypto", limit=3)
        print(f"Suggestions test: {len(test_suggestions)} suggestions found")
        
    except Exception as e:
        print(f"❌ Error during indexing: {e}")
        raise
    finally:
        # Close connections
        await mongodb_manager.close()
        await redis_manager.close()

if __name__ == "__main__":
    print("🚀 Starting task indexing...")
    asyncio.run(index_existing_tasks())
    print("✅ Indexing completed!")
