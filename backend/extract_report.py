#!/usr/bin/env python3
"""
Simple script to extract the latest research report from MongoDB and save to local file.
"""
import json
import os
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_latest_report():
    """Extract the latest research report from MongoDB"""
    try:
        # Connect to MongoDB
        mongodb_url = os.getenv('MONGODB_URL')
        if not mongodb_url:
            print("❌ MONGODB_URL not found in environment")
            return
        
        client = MongoClient(mongodb_url)
        db = client.research_assistant
        collection = db.tasks
        
        # Find the latest completed task
        latest_task = collection.find_one(
            {"status": "completed"},
            sort=[("created_at", -1)]
        )
        
        if not latest_task:
            print("❌ No completed tasks found")
            return
        
        print(f"✅ Found latest task: {latest_task.get('request_id')}")
        print(f"   Status: {latest_task.get('status')}")
        print(f"   Created: {latest_task.get('created_at')}")
        
        # Extract the result
        result = latest_task.get('result', {})
        if not result:
            print("❌ No result found in task")
            return
        
        print(f"   Result success: {result.get('success')}")
        
        # Extract final report
        final_report = result.get('final_report', {})
        if not final_report:
            print("❌ No final_report found in result")
            return
        
        print(f"   Final report keys: {list(final_report.keys())}")
        print(f"   Has mock marker: {'mock' in final_report}")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                "task_info": {
                    "request_id": latest_task.get('request_id'),
                    "status": latest_task.get('status'),
                    "created_at": latest_task.get('created_at'),
                    "completed_at": latest_task.get('completed_at')
                },
                "result": result,
                "final_report": final_report
            }, f, indent=2, default=str)
        
        print(f"✅ Report saved to: {filename}")
        print(f"   File size: {os.path.getsize(filename)} bytes")
        
        # Show final report structure
        print("\n📊 Final Report Structure:")
        print(f"   Type: {type(final_report)}")
        if isinstance(final_report, dict):
            print(f"   Keys: {list(final_report.keys())}")
            if 'mock' in final_report:
                print(f"   Mock marker: {final_report['mock']}")
            else:
                print("   ❌ No mock marker found")
        
        return filename
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None
    finally:
        if 'client' in locals():
            client.close()

if __name__ == "__main__":
    extract_latest_report()
