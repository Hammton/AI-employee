"""Test getting specific Asana actions"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def test_specific_actions():
    """Test getting specific Asana GET actions"""
    print("\n" + "=" * 70)
    print("TESTING SPECIFIC ASANA GET ACTIONS")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    user_id = "+254708235245@c.us"
    
    print(f"\nUser: {user_id}")
    
    # Try to get specific actions
    specific_actions = [
        "ASANA_GET_MULTIPLE_PROJECTS",
        "ASANA_GET_MULTIPLE_WORKSPACES",
        "ASANA_GET_MULTIPLE_TASKS",
        "ASANA_GET_A_PROJECT",
        "ASANA_GET_A_TASK"
    ]
    
    print("\n1. Trying to get specific actions...")
    try:
        # Try getting tools with specific actions using 'tools' parameter
        tools = composio_client.tools.get(
            user_id=user_id,
            tools=specific_actions
        )
        
        print(f"\n✓ Got {len(tools)} tools\n")
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_name = tool.name
            elif hasattr(tool, 'function'):
                tool_name = tool.function.get('name', 'unknown')
            else:
                tool_name = str(tool)
            print(f"   - {tool_name}")
        
    except Exception as e:
        print(f"\n✗ Error with specific actions: {e}")
        import traceback
        traceback.print_exc()
    
    # Try getting all tools without toolkit filter
    print("\n2. Trying to get tools without toolkit filter...")
    try:
        tools = composio_client.tools.get(
            user_id=user_id
        )
        
        print(f"\n✓ Got {len(tools)} tools total\n")
        
        # Filter for Asana
        asana_tools = []
        for tool in tools:
            if hasattr(tool, 'name'):
                tool_name = tool.name
            elif hasattr(tool, 'function') and hasattr(tool.function, 'name'):
                tool_name = tool.function['name']
            else:
                tool_name = str(tool)
            
            if 'ASANA' in tool_name:
                asana_tools.append(tool_name)
        
        print(f"   Asana tools found: {len(asana_tools)}\n")
        for tool_name in sorted(asana_tools)[:30]:
            print(f"   - {tool_name}")
        if len(asana_tools) > 30:
            print(f"   ... and {len(asana_tools) - 30} more")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_specific_actions()
