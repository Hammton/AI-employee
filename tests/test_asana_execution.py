"""Test if agent can actually execute Asana actions"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_asana_execution():
    """Test complete flow: connection check -> tool execution"""
    print("\n" + "=" * 70)
    print("TESTING ASANA TOOL EXECUTION")
    print("=" * 70)
    
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    
    # Create kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["asana"])
    print("   OK Kernel initialized")
    
    # Check connection
    print("\n2. Checking Asana connection...")
    is_connected = kernel.check_connection("asana")
    print(f"   {'OK' if is_connected else 'FAIL'} Connected: {is_connected}")
    
    if not is_connected:
        print("\n   ERROR: Not connected to Asana!")
        print("   Please connect first using /connect asana")
        return
    
    # Check what tools are available
    print("\n3. Checking available tools...")
    if kernel.agent_executor:
        # Get tools from the agent
        print("   Agent executor created successfully")
    else:
        print("   ERROR: Agent executor not created")
        return
    
    # Test simple query
    print("\n4. Testing query: 'List my Asana tasks'")
    print("   (This will show detailed execution logs)")
    print("-" * 70)
    
    try:
        result = kernel.run("List my Asana tasks")
        
        print("-" * 70)
        print("\n5. RESULT:")
        print(result)
        
        if "error" in result.lower() or "failed" in result.lower():
            print("\n   STATUS: FAIL - Error in execution")
        elif "task" in result.lower() or "asana" in result.lower():
            print("\n   STATUS: SUCCESS - Got Asana data!")
        else:
            print("\n   STATUS: PARTIAL - Got response but unclear if it worked")
            
    except Exception as e:
        print("-" * 70)
        print(f"\n5. ERROR: {e}")
        print("\n   STATUS: FAIL - Exception during execution")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_asana_execution()
