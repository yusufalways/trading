#!/usr/bin/env python3
"""
Test script to verify remember me functionality
Run this to test the authentication system independently
"""

import json
import os
from datetime import datetime

def test_remember_me_file():
    """Test if remember me file can be created and read"""
    remember_file = "data/remember_me.json"
    
    # Test data
    test_data = {
        "token": "test_token_123",
        "email": "test@example.com",
        "created": datetime.now().isoformat()
    }
    
    try:
        # Create directory if needed
        os.makedirs(os.path.dirname(remember_file), exist_ok=True)
        
        # Write test data
        with open(remember_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print("✅ Successfully created remember me file")
        
        # Read test data
        with open(remember_file, 'r') as f:
            loaded_data = json.load(f)
        
        print("✅ Successfully read remember me file")
        print(f"📧 Email: {loaded_data.get('email')}")
        print(f"🔑 Token: {loaded_data.get('token')}")
        print(f"📅 Created: {loaded_data.get('created')}")
        
        # Clean up
        os.remove(remember_file)
        print("✅ Successfully cleaned up test file")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing remember me functionality: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Remember Me File Operations...")
    print("=" * 50)
    
    success = test_remember_me_file()
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Remember me functionality should work.")
    else:
        print("💥 Tests failed! Check file permissions and directory access.")
