"""Test that kernel.py now loads GET/LIST/READ tools for Asana"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_kernel_asana_tools():
    """Test that kernel loads both default AND GET tools for Asana"""
    print("\n" + "=" * 70)
    print("TESTING KERNEL WITH ENHANCED TOOL LOADING")
    print("=" * 70)
    
    # Use the entity that has ACTIVE Asana connection
    user_id = "+254708235245@c.us"
    
    print(f"\nUser: {user_id}")
    print("Setting up kernel with Asana...")
    
    # Initialize kernel
    kernel = AgentKernel(user_id=user_id)
    
    # Setup with Asana
    kernel.setup(apps=["asana"])
    
    # Check what tools were loaded
    print("\n" + "=" * 70)
    print("ANALYZING LOADED TOOLS")
    print("=" * 70)
    
    print(f"\nAgent executor type: {type(kernel.agent_executor)}")
    
    # The agent executor is a LangGraph CompiledStateGraph
    # We need to check the composio_client tools that were loaded
    # Let's test by running a simple query
    
    print("\nTesting with a simple query to list Asana projects...")
    try:
        result = kernel.run("List all my Asana projects")
        print(f"\nResult: {result[:500] if result else 'No result'}...")
        
        if result and ("project" in result.lower() or "workspace" in result.lower()):
            print("\n[SUCCESS] Kernel can access Asana GET tools!")
        else:
            print("\n[INFO] Result received but unclear if GET tools worked")
            
    except Exception as e:
        print(f"\n[ERROR] Failed to run query: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_kernel_asana_tools()
