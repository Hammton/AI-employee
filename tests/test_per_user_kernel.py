"""
Test Per-User Kernel Management
Verifies that each user gets their own kernel with unique entity_id
"""
import os
from dotenv import load_dotenv

load_dotenv()

from kernel import AgentKernel

print("=" * 80)
print("🧪 PER-USER KERNEL TEST")
print("=" * 80)

# Simulate 3 different WhatsApp users
users = [
    {"name": "Alice", "phone": "+1234567890"},
    {"name": "Bob", "phone": "+0987654321"},
    {"name": "Charlie", "phone": "+1122334455"},
]

user_kernels = {}

def get_kernel_for_user(user_id: str) -> AgentKernel:
    """Get or create a kernel instance for a specific user."""
    if user_id not in user_kernels:
        print(f"\n🔧 Creating new kernel for user: {user_id}")
        user_kernels[user_id] = AgentKernel(user_id=user_id)
    return user_kernels[user_id]

print("\n" + "=" * 80)
print("PHASE 1: CREATE KERNELS FOR EACH USER")
print("=" * 80)

for user in users:
    print(f"\n👤 User: {user['name']} ({user['phone']})")
    kernel = get_kernel_for_user(user['phone'])
    print(f"   ✅ Kernel created with user_id: {kernel.user_id}")

print("\n" + "=" * 80)
print("PHASE 2: GENERATE AUTH URLS (Should show unique entity_id)")
print("=" * 80)

for user in users:
    print(f"\n👤 {user['name']} wants to connect Asana")
    kernel = get_kernel_for_user(user['phone'])
    
    try:
        auth_url = kernel.get_auth_url("asana")
        
        # Check if URL contains the correct entity_id
        if user['phone'] in auth_url:
            print(f"   ✅ CORRECT: URL contains user's phone number")
            print(f"   🔗 {auth_url}")
        elif "default_user" in auth_url:
            print(f"   ❌ WRONG: URL still shows 'default_user'")
            print(f"   🔗 {auth_url}")
        else:
            print(f"   ⚠️  UNEXPECTED: URL format changed")
            print(f"   🔗 {auth_url}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print("\n" + "=" * 80)
print("PHASE 3: VERIFY KERNEL REUSE")
print("=" * 80)

print("\n🔄 Alice requests Asana connection again...")
kernel1 = get_kernel_for_user(users[0]['phone'])
kernel2 = get_kernel_for_user(users[0]['phone'])

if kernel1 is kernel2:
    print("   ✅ CORRECT: Same kernel instance reused (efficient)")
else:
    print("   ❌ WRONG: New kernel created (memory leak)")

print(f"\n📊 Total kernels in memory: {len(user_kernels)}")
print(f"   Expected: 3 (one per user)")
print(f"   Actual: {len(user_kernels)}")

if len(user_kernels) == 3:
    print("   ✅ CORRECT: Efficient memory usage")
else:
    print("   ❌ WRONG: Memory leak detected")

print("\n" + "=" * 80)
print("PHASE 4: TEST DIFFERENT TOOLS")
print("=" * 80)

tools_to_test = ["gmail", "google calendar", "slack"]

for tool in tools_to_test:
    print(f"\n🔧 Testing: {tool}")
    kernel = get_kernel_for_user(users[0]['phone'])
    
    try:
        auth_url = kernel.get_auth_url(tool)
        
        if users[0]['phone'] in auth_url:
            print(f"   ✅ {tool}: Correct entity_id")
        else:
            print(f"   ❌ {tool}: Wrong entity_id")
            print(f"      URL: {auth_url[:80]}...")
    except Exception as e:
        print(f"   ⚠️  {tool}: {e}")

print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)

print("\n✅ Expected Behavior:")
print("   • Each user gets their own kernel instance")
print("   • Auth URLs contain user's phone number as entity_id")
print("   • Kernel instances are reused (not recreated)")
print("   • All tools work with correct entity_id")

print("\n🎯 This fixes the issue where:")
print("   • All users shared 'default_user' entity_id")
print("   • Tool connections were mixed between users")
print("   • Auth URLs showed wrong entity_id")

print("\n💡 Integration with main.py:")
print("   • Add: user_kernels = {} (global dict)")
print("   • Add: get_kernel_for_user(user_id) function")
print("   • Update: generate_response_for_payload(sender_id=...)")
print("   • Use: kernel = get_kernel_for_user(sender_name)")

print("\n" + "=" * 80)
print("TEST COMPLETE!")
print("=" * 80)
print()
