"""Check what Google Docs tools are available in Composio"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

def check_googledocs_tools():
    """Check available Google Docs tools"""
    print("\n" + "=" * 70)
    print("CHECKING GOOGLE DOCS TOOLS IN COMPOSIO")
    print("=" * 70)
    
    composio_client = Composio(api_key=os.environ.get("COMPOSIO_API_KEY"))
    user_id = "+254708235245@c.us"
    
    print(f"\nUser: {user_id}")
    
    # Get default toolkit tools
    print("\n1. Getting default GOOGLEDOCS toolkit tools...")
    try:
        toolkit_tools = composio_client.tools.get(
            user_id=user_id,
            toolkits=["GOOGLEDOCS"]
        )
        
        print(f"\nFound {len(toolkit_tools)} default tools:")
        for tool in toolkit_tools:
            if hasattr(tool, 'name'):
                tool_name = tool.name
            elif hasattr(tool, 'function'):
                tool_name = tool.function.get('name', 'unknown')
            else:
                tool_name = str(tool)
            print(f"   - {tool_name}")
    except Exception as e:
        print(f"\nError: {e}")
    
    # Try to get specific CREATE/UPDATE tools
    print("\n2. Checking for CREATE/UPDATE tools...")
    create_tools = [
        'GOOGLEDOCS_CREATE_DOCUMENT',
        'GOOGLEDOCS_UPDATE_DOCUMENT',
        'GOOGLEDOCS_APPEND_TEXT',
        'GOOGLEDOCS_INSERT_TEXT',
        'GOOGLEDOCS_BATCH_UPDATE',
        'GOOGLEDOCS_CREATE_BLANK_DOCUMENT',
    ]
    
    for tool_name in create_tools:
        try:
            tools = composio_client.tools.get(
                user_id=user_id,
                tools=[tool_name]
            )
            if tools:
                print(f"   ✓ {tool_name} - EXISTS")
        except Exception as e:
            print(f"   ✗ {tool_name} - NOT FOUND")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_googledocs_tools()
