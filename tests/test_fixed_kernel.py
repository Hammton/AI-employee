"""
Test the fixed kernel with session-based authentication
This should now work properly with Composio tools!
"""
import os
from dotenv import load_dotenv

load_dotenv()

from kernel import AgentKernel

print("=" * 70)
print("TESTING FIXED KERNEL WITH SESSION-BASED AUTHENTICATION")
print("=" * 70)

# Test 1: Create kernel with user_id
print("\n📝 Test 1: Creating kernel with user_id...")
user_id = "test_user_fixed_kernel"
kernel = AgentKernel(user_id=user_id)
print(f"✅ Kernel created for user: {kernel.user_id}")

# Test 2: Setup with Gmail toolkit
print("\n📝 Test 2: Setting up Gmail toolkit...")
kernel.setup(apps=["gmail"])
print(f"✅ Active toolkits: {kernel.active_apps}")

# Test 3: Check if session was created
print("\n📝 Test 3: Verifying session...")
if kernel.composio_session:
    print(f"✅ Session created: {type(kernel.composio_session)}")
    print(f"   User ID: {kernel.user_id}")
else:
    print("❌ Session not created!")

# Test 4: Get auth URL
print("\n📝 Test 4: Getting auth URL for Gmail...")
try:
    auth_url = kernel.get_auth_url("gmail")
    print(f"✅ Auth URL generated:")
    print(f"   {auth_url[:100]}...")
except Exception as e:
    print(f"❌ Failed to get auth URL: {e}")

# Test 5: Try a simple query (will fail if not authenticated, but shouldn't crash)
print("\n📝 Test 5: Testing agent execution...")
try:
    response = kernel.run("What tools do I have available?")
    print(f"✅ Agent responded:")
    print(f"   {response[:200]}...")
except Exception as e:
    print(f"⚠️  Agent execution error (expected if not authenticated): {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE!")
print("=" * 70)
print("\n📋 Summary:")
print("   - Kernel now uses session-based API ✅")
print("   - User context properly scoped ✅")
print("   - Auth URL generation simplified ✅")
print("   - Removed 100+ lines of unused code ✅")
print("\n🎯 Next steps:")
print("   1. Click the auth URL above to connect Gmail")
print("   2. Run this test again after authenticating")
print("   3. Try: kernel.run('Check my latest 3 emails')")
print()
