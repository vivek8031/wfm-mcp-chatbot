# run_tests.py - Simple test runner for WFM system
"""
Simple test runner that doesn't require pytest
Run: python run_tests.py
"""

import asyncio
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from test_wfm_integration import run_all_tests

async def main():
    """Run all WFM tests"""
    print("=" * 60)
    print("🚀 WFM Database Assistant - Test Suite")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check environment
    required_vars = ["MONGODB_CONNECTION_STRING"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set the following in your .env file:")
        for var in missing_vars:
            print(f"  {var}=your_value_here")
        return False
    
    # Optional variables
    optional_vars = ["ANTHROPIC_API_KEY"]
    for var in optional_vars:
        if not os.getenv(var):
            print(f"⚠️  Optional variable not set: {var} (some tests will be skipped)")
    
    print("\n🧪 Running integration tests...\n")
    
    # Run tests
    success = await run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("Your WFM Database Assistant is ready to use.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check the output above for errors.")
    
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)