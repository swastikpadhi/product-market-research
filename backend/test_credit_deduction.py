#!/usr/bin/env python3
"""
Test script to validate credit deduction logic
This script tests the credit deduction without spending credits
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

def test_credit_transaction_creation():
    """Test that CreditTransaction can be created without description field"""
    logger.info("🧪 Testing CreditTransaction creation...")
    
    try:
        from app.models.postgres_models import CreditTransaction
        import uuid
        
        # Test creating a CreditTransaction with valid fields only
        transaction = CreditTransaction(
            transaction_id=f"txn_{uuid.uuid4().hex[:12]}",
            balance_id=str(uuid.uuid4()),
            amount=-6,  # Negative for deduction
            balance_after=94,
            research_request_id="test_request_123",
            research_depth="basic"
        )
        
        logger.info("  ✅ CreditTransaction created successfully!")
        logger.info(f"    Transaction ID: {transaction.transaction_id}")
        logger.info(f"    Amount: {transaction.amount}")
        logger.info(f"    Balance After: {transaction.balance_after}")
        logger.info(f"    Research Request ID: {transaction.research_request_id}")
        logger.info(f"    Research Depth: {transaction.research_depth}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ CreditTransaction creation failed: {e}")
        return False

def test_credit_service_initialization():
    """Test credit service initialization"""
    logger.info("🧪 Testing credit service initialization...")
    
    try:
        from app.db.database_factory import celery_context
        from app.services.credit_service import credit_service
        
        with celery_context():
            # Test credit service initialization
            logger.info("  Testing credit service initialization...")
            credit_service._ensure_initialized()
            
            if credit_service.repository is not None:
                logger.info("  ✅ Credit service initialized successfully!")
                return True
            else:
                logger.error("  ❌ Credit service repository is None")
                return False
                
    except Exception as e:
        logger.error(f"❌ Credit service initialization test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting credit deduction validation...")
    
    tests = [
        ("CreditTransaction Creation", test_credit_transaction_creation),
        ("Credit Service Initialization", test_credit_service_initialization)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name} PASSED")
            else:
                logger.error(f"❌ {test_name} FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name} ERROR: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nTotal: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! Credit deduction should work correctly.")
        return True
    else:
        logger.error("💥 Some tests failed. Please fix the issues before running research tasks.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
