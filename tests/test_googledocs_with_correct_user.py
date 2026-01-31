"""Test Google Docs with the correct user ID that has connections"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_with_correct_user():
    """Test with user ID that actually has Google Docs connected"""
    print("\n" + "=" * 70)
    print("TESTING WITH CORRECT USER ID")
    print("=" * 70)
    
    # This is the user_id that has Google Docs connected (from inspection)
    user_id = "86152916787450@lid"
    print(f"\nUser: {user_id}")
    
    # Initialize kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    
    # Setup kernel (should auto-detect connected apps)
    print("\n2. Setting up kernel (auto-detecting connected apps)...")
    kernel.setup()
    
    # Check what apps were detected
    print(f"\n3. Auto-detected apps: {kernel.active_apps}")
    
    # Check tools
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
            print("\n   ✅ Google Docs tools found:")
            for tool in googledocs_tools[:10]:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                print(f"      - {tool_name}")
        else:
            print("\n   ❌ NO GOOGLE DOCS TOOLS FOUND!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_with_correct_user()
