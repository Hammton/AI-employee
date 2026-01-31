"""Find where the browser tool is coming from"""
import os
from dotenv import load_dotenv
from composio import Composio
from composio_langchain import LangchainProvider

load_dotenv()

def find_browser_tool():
    """Search for browser tools"""
    print("\n" + "=" * 70)
    print("SEARCHING FOR BROWSER TOOLS")
    print("=" * 70)
    
    user_id = "86152916787450@lid"
    print(f"\nUser: {user_id}")
    
    composio_client = Composio(
        api_key=os.environ.get("COMPOSIO_API_KEY"),
        provider=LangchainProvider()
    )
    
    # Check connected accounts
    print("\n1. Checking connected accounts...")
    connected_accounts = composio_client.connected_accounts.list(
        user_ids=[user_id]
    )
    
    for account in connected_accounts.items:
        if account.status == "ACTIVE":
            toolkit_slug = getattr(account.toolkit, 'slug', 'unknown') if hasattr(account, 'toolkit') and account.toolkit else 'unknown'
            print(f"   - {toolkit_slug.upper()}: {account.status}")
    
    # Try to get browser tools
    print("\n2. Attempting to get ANCHOR_BROWSER tools...")
    try:
        tools = composio_client.tools.get(
            user_id=user_id,
            toolkits=["ANCHOR_BROWSER"]
        )
        print(f"   [OK] Got {len(tools)} browser tools")
        for tool in tools[:5]:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            print(f"      - {tool_name}")
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    # Check if browser tools are in default toolkit list
    print("\n3. Checking default tools (no toolkit specified)...")
    try:
        # Get tools for connected apps only
        connected_slugs = []
        for account in connected_accounts.items:
            if account.status == "ACTIVE":
                toolkit_slug = getattr(account.toolkit, 'slug', '').upper()
                if toolkit_slug and toolkit_slug not in connected_slugs:
                    connected_slugs.append(toolkit_slug)
        
        print(f"   Connected toolkits: {connected_slugs}")
        
        all_tools = []
        for toolkit in connected_slugs:
            try:
                tools = composio_client.tools.get(
                    user_id=user_id,
                    toolkits=[toolkit]
                )
                print(f"   {toolkit}: {len(tools)} tools")
                all_tools.extend(tools)
            except Exception as e:
                print(f"   {toolkit}: ERROR - {e}")
        
        # Check if any browser tools snuck in
        browser_tools = [t for t in all_tools if 'BROWSER' in str(t.name if hasattr(t, 'name') else t).upper() or 'ANCHOR' in str(t.name if hasattr(t, 'name') else t).upper()]
        
        if browser_tools:
            print(f"\n   [FOUND] {len(browser_tools)} browser tools in loaded tools:")
            for tool in browser_tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                print(f"      - {tool_name}")
        else:
            print(f"\n   [OK] No browser tools found in loaded tools")
    
    except Exception as e:
        print(f"   [ERROR] {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    find_browser_tool()
