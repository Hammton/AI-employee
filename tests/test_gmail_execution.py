"""Test Gmail execution with the updated kernel"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_gmail_execution():
    """Test Gmail tool execution"""
    print("\n" + "=" * 70)
    print("TESTING GMAIL TOOL EXECUTION")
    print("=" * 70)
    
    # Use the user ID that has Gmail connected
    user_id = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"
    print(f"\nUser: {user_id}")
    
    # Create kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["gmail"])
    print("   OK Kernel initialized")
    
    # Check connection
    print("\n2. Checking Gmail connection...")
    is_connected = kernel.check_connection("gmail")
    print(f"   {'OK' if is_connected else 'FAIL'} Connected: {is_connected}")
    
    if not is_connected:
        print("\n   ERROR: Not connected to Gmail!")
        print("   This user should have Gmail connected")
        return
    
    # Test query
    print("\n3. Testing query: 'Check my latest 3 Gmail emails'")
    print("   (This will show detailed execution logs)")
    print("-" * 70)
    
    try:
        result = kernel.run("Please check my latest 3 Gmail emails and tell me who they're from and what they're about.")
        
        print("-" * 70)
        print("\n4. RESULT:")
        print(result)
        
        if "error" in result.lower() and "json" in result.lower():
            print("\n   STATUS: FAIL - Same JSON serialization error")
        elif "email" in result.lower() or "from" in result.lower() or "subject" in result.lower():
            print("\n   STATUS: SUCCESS - Got Gmail data!")
        else:
            print("\n   STATUS: PARTIAL - Got response but unclear if it worked")
            
    except Exception as e:
        print("-" * 70)
        print(f"\n4. ERROR: {e}")
        
        if "JSON serializable" in str(e):
            print("\n   STATUS: FAIL - Same Composio bug")
        else:
            print("\n   STATUS: FAIL - Different error")
        
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_gmail_execution()
