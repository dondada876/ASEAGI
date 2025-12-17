#!/usr/bin/env python3
"""
Test Vtiger CRM Connection
Tests authentication and basic operations
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from integrations.vtiger_sync import VtigerIntegration

def main():
    print("\n🧪 VTIGER CONNECTION TEST SCRIPT")
    print("=" * 70)
    
    # Create integration instance
    vtiger = VtigerIntegration()
    
    # Test connection
    success = vtiger.test_connection()
    
    if success:
        print("\n🎉 All tests passed!")
        print("\nYou can now:")
        print("  1. Create tickets from bugs automatically")
        print("  2. Sync bug status to Vtiger")
        print("  3. Query tickets from your CRM")
        sys.exit(0)
    else:
        print("\n❌ Connection test failed")
        print("\nTroubleshooting:")
        print("  1. Check .env file has correct Vtiger credentials")
        print("  2. Verify VTIGER_ENABLED=true")
        print("  3. Test Vtiger URL is accessible")
        print("  4. Verify username and access key are correct")
        print("\nExample .env configuration:")
        print("  VTIGER_ENABLED=true")
        print("  VTIGER_URL=https://your-crm.od2.vtiger.com")
        print("  VTIGER_USERNAME=admin")
        print("  VTIGER_ACCESS_KEY=your_access_key_here")
        sys.exit(1)

if __name__ == "__main__":
    main()
