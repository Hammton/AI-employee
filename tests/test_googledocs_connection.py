"""Test Google Docs connection and tool loading"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_googledocs_connection():
    """Test if Google Docs tools are loaded for connected user"""
    print("\n" + "=" * 70)
    print("TESTING GOOGLE DOCS CONNECTION AND TOOL LOADING")
    print("=" * 70)
    
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    
    # Initialize kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    
    # Check if Google Docs is connected
    print("\n2. Checking Google Docs connection...")
    is_connected = kernel.check_connection("googledocs")
    print(f"   Google Docs connected: {is_connected}")
    
    # Setup kernel with no apps (default)
    print("\n3. Setting up kernel with no apps...")
    kernel.setup()
    
    # Check what tools are available
    print("\n4. Checking available tools...")
    if kernel.agent_executor:
        tools = kernel.agent_executor.tools if hasattr(kernel.agent_executor, 'tools') else []
        print(f"   Total tools: {len(tools)}")
        
        # Look for Google Docs tools
        googledocs_tools = [t for t in tools if 'GOOGLEDOCS' in str(t.name if hasattr(t, 'name') else t)]
        googlesheets_tools = [t for t in tools if 'GOOGLESHEETS' in str(t.name if hasattr(t, 'name') else t)]
        
        print(f"   Google Docs tools: {len(googledocs_tools)}")
        print(f"   Google Sheets tools: {len(googlesheets_tools)}")
        
        if googledocs_tools:
            print("\n   Google Docs tools found:")
            for tool in googledocs_tools[:5]:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                print(f"      - {tool_name}")
        else:
            print("\n   ❌ NO GOOGLE DOCS TOOLS FOUND!")
            print("   This is the problem - user is connected but tools not loaded")
    
    # Now explicitly add Google Docs
    print("\n5. Explicitly adding Google Docs toolkit...")
    kernel.add_apps(['googledocs'])
    
    # Check tools again
    print("\n6. Checking tools after explicit add...")
    if kernel.agent_executor:
        tools = kernel.agent_executor.tools if hasattr(kernel.agent_executor, 'tools') else []
        print(f"   Total tools: {len(tools)}")
        
        googledocs_tools = [t for t in tools if 'GOOGLEDOCS' in str(t.name if hasattr(t, 'name') else t)]
        print(f"   Google Docs tools: {len(googledocs_tools)}")
        
        if googledocs_tools:
            print("\n   ✅ Google Docs tools NOW loaded:")
            for tool in googledocs_tools[:10]:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                print(f"      - {tool_name}")
    
    print("\n" + "=" * 70)
    print("CONCLUSION:")
    print("The issue is that connected apps are not automatically loaded.")
    print("User must explicitly call generate_auth_link or check_app_connection")
    print("for the tools to be loaded, even if already connected.")
    print("=" * 70)

if __name__ == "__main__":
    test_googledocs_connection()
