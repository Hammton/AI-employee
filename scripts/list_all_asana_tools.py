"""List ALL available Asana tools from Composio"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def list_asana_tools():
    """List all Asana tools available in Composio"""
    print("\n" + "=" * 70)
    print("LISTING ALL ASANA TOOLS FROM COMPOSIO")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    user_id = "+254708235245@c.us"
    
    print(f"\nUser: {user_id}")
    print("\nFetching Asana tools...")
    
    try:
        # Get tools using the antigravity pattern
        tools = composio_client.tools.get(
            user_id=user_id,
            toolkits=["asana"]
        )
        
        print(f"\n✓ Found {len(tools)} Asana tools\n")
        
        # Categorize tools
        get_tools = []
        create_tools = []
        delete_tools = []
        update_tools = []
        other_tools = []
        
        for tool in tools:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            
            if 'GET' in tool_name or 'RETRIEVE' in tool_name or 'LIST' in tool_name:
                get_tools.append(tool_name)
            elif 'CREATE' in tool_name or 'ADD' in tool_name:
                create_tools.append(tool_name)
            elif 'DELETE' in tool_name or 'REMOVE' in tool_name:
                delete_tools.append(tool_name)
            elif 'UPDATE' in tool_name or 'MODIFY' in tool_name:
                update_tools.append(tool_name)
            else:
                other_tools.append(tool_name)
        
        print(f"📖 GET/READ/LIST Tools ({len(get_tools)}):")
        for tool in sorted(get_tools):
            print(f"   - {tool}")
        
        print(f"\n➕ CREATE/ADD Tools ({len(create_tools)}):")
        for tool in sorted(create_tools)[:10]:  # Show first 10
            print(f"   - {tool}")
        if len(create_tools) > 10:
            print(f"   ... and {len(create_tools) - 10} more")
        
        print(f"\n🗑️  DELETE/REMOVE Tools ({len(delete_tools)}):")
        for tool in sorted(delete_tools):
            print(f"   - {tool}")
        
        print(f"\n✏️  UPDATE/MODIFY Tools ({len(update_tools)}):")
        for tool in sorted(update_tools):
            print(f"   - {tool}")
        
        if other_tools:
            print(f"\n🔧 Other Tools ({len(other_tools)}):")
            for tool in sorted(other_tools):
                print(f"   - {tool}")
        
        # Check for specific tools we need
        print("\n" + "=" * 70)
        print("CHECKING FOR SPECIFIC TOOLS WE NEED:")
        print("=" * 70)
        
        all_tool_names = [t.name if hasattr(t, 'name') else str(t) for t in tools]
        
        needed_tools = [
            'ASANA_GET_MULTIPLE_PROJECTS',
            'ASANA_GET_MULTIPLE_WORKSPACES',
            'ASANA_GET_MULTIPLE_TASKS',
            'ASANA_GET_A_PROJECT',
            'ASANA_GET_A_TASK'
        ]
        
        for tool_name in needed_tools:
            found = tool_name in all_tool_names
            status = "✓ FOUND" if found else "✗ NOT FOUND"
            print(f"   {tool_name:40} {status}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    list_asana_tools()
