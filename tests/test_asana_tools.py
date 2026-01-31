"""
Test what Asana tools are available for the connected user
"""

import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_asana_tools():
    """Check what Asana tools are available."""
    print("\n" + "=" * 70)
    print("TESTING ASANA TOOLS")
    print("=" * 70)
    
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    
    # Create kernel
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["asana"])
    
    print("\n1. Checking connection...")
    is_connected = kernel.check_connection("asana")
    print(f"   {'OK' if is_connected else 'NOT OK'} Connected: {is_connected}")
    
    if not is_connected:
        print("\n   WARNING: User is not connected to Asana!")
        print("   Please connect first using /connect asana")
        return
    
    print("\n2. Getting available tools...")
    try:
        # Get tools from session
        tools = kernel.composio_session.tools()
        
        print(f"   OK Found {len(tools)} total tools")
        
        # Filter Asana tools
        asana_tools = [tool for tool in tools if 'asana' in str(tool.name).lower()]
        
        if not asana_tools:
            print("   NOT OK No Asana tools found!")
        else:
            print(f"   OK Found {len(asana_tools)} Asana tools:")
            
            for i, tool in enumerate(asana_tools[:10], 1):  # Show first 10
                print(f"\n   Tool #{i}:")
                print(f"      Name: {tool.name}")
                if hasattr(tool, 'description'):
                    desc = str(tool.description)[:100]
                    print(f"      Description: {desc}...")
        
    except Exception as e:
        print(f"   NOT OK Error getting tools: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n3. Testing a simple query...")
    try:
        query = "List my Asana tasks"
        print(f"   Query: {query}")
        
        result = kernel.run(query)
        print(f"\n   Response:")
        print(f"   {result[:500]}...")
        
    except Exception as e:
        print(f"   NOT OK Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_asana_tools()
