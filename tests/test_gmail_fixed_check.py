"""Test Gmail with fixed connection check"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_gmail_fixed():
    """Test Gmail with fixed name mapping"""
    print("\n" + "=" * 70)
    print("TESTING GMAIL WITH FIXED CONNECTION CHECK")
    print("=" * 70)
    
    user_id = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"
    print(f"\nUser: {user_id}")
    
    # Create kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["gmail"])
    print("   OK Kernel initialized")
    
    # Test different name variations
    print("\n2. Testing name variations...")
    variations = ['gmail', 'googlemail', 'google_mail', 'Google Mail']
    
    for name in variations:
        is_connected = kernel.check_connection(name)
        status = "OK CONNECTED" if is_connected else "FAIL NOT CONNECTED"
        print(f"   {name:20} -> {status}")
    
    # Now test the agent
    print("\n3. Testing agent with Gmail query...")
    print("-" * 70)
    
    try:
        result = kernel.run("Check my latest 3 Gmail emails and tell me who they're from.")
        
        print("-" * 70)
        print("\n4. RESULT:")
        print(result)
        
        # Check if it worked
        if "connect" in result.lower() and "gmail" in result.lower():
            print("\n   STATUS: FAIL - Still asking to connect")
        elif "email" in result.lower() or "from" in result.lower() or "subject" in result.lower():
            print("\n   STATUS: SUCCESS - Got Gmail data!")
        else:
            print("\n   STATUS: PARTIAL - Got response")
            
    except Exception as e:
        print("-" * 70)
        print(f"\n4. ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_gmail_fixed()
