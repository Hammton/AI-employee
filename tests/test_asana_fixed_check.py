"""Test Asana with fixed connection check"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_asana_fixed():
    """Test Asana with fixed name mapping"""
    print("\n" + "=" * 70)
    print("TESTING ASANA WITH FIXED CONNECTION CHECK")
    print("=" * 70)
    
    # Test with the entity that has ACTIVE Asana connection
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    print("(This entity has an ACTIVE Asana connection)")
    
    # Create kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["asana"])
    print("   ✓ Kernel initialized")
    
    # Test different name variations
    print("\n2. Testing name variations...")
    variations = ['asana', 'Asana', 'ASANA']
    
    for name in variations:
        is_connected = kernel.check_connection(name)
        status = "✓ CONNECTED" if is_connected else "✗ NOT CONNECTED"
        print(f"   {name:20} -> {status}")
    
    # Now test the agent
    print("\n3. Testing agent with Asana query...")
    print("-" * 70)
    
    try:
        result = kernel.run("List my Asana tasks or projects. Show me what's in my Asana workspace.")
        
        print("-" * 70)
        print("\n4. RESULT:")
        print(result)
        
        # Check if it worked
        if "connect" in result.lower() and "asana" in result.lower() and "auth" in result.lower():
            print("\n   STATUS: ✗ FAIL - Still asking to connect")
        elif "task" in result.lower() or "project" in result.lower() or "workspace" in result.lower():
            print("\n   STATUS: ✓ SUCCESS - Got Asana data!")
        else:
            print("\n   STATUS: ⚠ PARTIAL - Got response")
            
    except Exception as e:
        print("-" * 70)
        print(f"\n4. ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    
    # Also show the issue with the test user
    print("\n" + "=" * 70)
    print("ISSUE WITH TEST USER")
    print("=" * 70)
    
    test_user = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"
    print(f"\nUser: {test_user}")
    print("This user has Asana in INITIALIZING status (OAuth not completed)")
    
    kernel2 = AgentKernel(user_id=test_user)
    kernel2.setup(apps=["asana"])
    
    is_connected = kernel2.check_connection("asana")
    print(f"\nConnection check: {'✓ CONNECTED' if is_connected else '✗ NOT CONNECTED'}")
    print("\nNote: Connection is INITIALIZING, not ACTIVE.")
    print("To fix: Complete the OAuth flow in Composio dashboard.")
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_asana_fixed()
