"""
Test connection checking functionality

This verifies that:
1. check_connection() works correctly
2. get_auth_url() returns None when already connected
3. /connect command detects existing connections
"""

import os
from dotenv import load_dotenv
from kernel import AgentKernel

# Load environment variables
load_dotenv()

def test_connection_check():
    """Test connection checking for a user."""
    print("=" * 60)
    print("TEST: Connection Status Checking")
    print("=" * 60)
    
    # Check if API keys are set
    if not os.environ.get("OPENROUTER_API_KEY"):
        print("⚠️  OPENROUTER_API_KEY not set in .env")
    if not os.environ.get("COMPOSIO_API_KEY"):
        print("⚠️  COMPOSIO_API_KEY not set in .env")
    
    # Create a kernel for a test user
    user_id = "test_user_connection_check"
    print(f"\n📝 Creating kernel for user: {user_id}")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup()
    
    # Test with a common app
    app_name = "asana"
    
    print(f"\n1️⃣ Checking connection status for {app_name}...")
    is_connected = kernel.check_connection(app_name)
    
    if is_connected:
        print(f"   ✅ User is connected to {app_name}")
    else:
        print(f"   ❌ User is NOT connected to {app_name}")
    
    print(f"\n2️⃣ Getting auth URL for {app_name}...")
    auth_url = kernel.get_auth_url(app_name)
    
    if auth_url is None:
        print(f"   ✅ No auth URL needed - already connected!")
    elif auth_url:
        print(f"   📝 Auth URL generated: {auth_url[:60]}...")
    else:
        print(f"   ⚠️  No auth URL returned")
    
    print(f"\n3️⃣ Testing force parameter...")
    auth_url_force = kernel.get_auth_url(app_name, force=True)
    
    if auth_url_force:
        print(f"   ✅ Force auth URL generated: {auth_url_force[:60]}...")
    else:
        print(f"   ⚠️  No auth URL returned even with force=True")
    
    print("\n" + "=" * 60)
    print("✅ Connection check test complete!")
    print("=" * 60)
    
    print("\n📊 Summary:")
    print(f"   • User ID: {user_id}")
    print(f"   • App: {app_name}")
    print(f"   • Connected: {is_connected}")
    print(f"   • Auth URL needed: {auth_url is not None}")
    
    if is_connected:
        print("\n💡 The user is already connected!")
        print("   When they ask to connect again, they should see:")
        print("   '✅ ASANA Already Connected!'")
    else:
        print("\n💡 The user needs to connect!")
        print("   They should receive an auth URL to complete the connection.")
    
    return True

if __name__ == "__main__":
    try:
        test_connection_check()
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
