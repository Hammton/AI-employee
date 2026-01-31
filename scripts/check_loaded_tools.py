"""Check what tools are actually loaded in the kernel"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def check_loaded_tools():
    """Check loaded tools"""
    print("\n" + "=" * 70)
    print("CHECKING LOADED TOOLS")
    print("=" * 70)
    
    user_id = "86152916787450@lid"
    print(f"\nUser: {user_id}")
    
    # Initialize and setup kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup()
    
    print(f"\n2. Active apps: {kernel.active_apps}")
    
    # Check agent executor
    if kernel.agent_executor:
        print("\n3. Agent executor created successfully")
        
        # Try to access tools
        if hasattr(kernel.agent_executor, 'tools'):
            tools = kernel.agent_executor.tools
            print(f"\n4. Total tools: {len(tools)}")
            
            # Group by toolkit
            by_toolkit = {}
            for tool in tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                # Extract toolkit prefix
                if '_' in tool_name:
                    toolkit = tool_name.split('_')[0]
                else:
                    toolkit = 'OTHER'
                
                if toolkit not in by_toolkit:
                    by_toolkit[toolkit] = []
                by_toolkit[toolkit].append(tool_name)
            
            print(f"\n5. Tools by toolkit:")
            for toolkit, tool_list in sorted(by_toolkit.items()):
                print(f"\n   {toolkit}: {len(tool_list)} tools")
                for tool_name in tool_list[:5]:
                    print(f"      - {tool_name}")
                if len(tool_list) > 5:
                    print(f"      ... and {len(tool_list) - 5} more")
        else:
            print("\n4. Agent executor has no 'tools' attribute")
            print(f"   Attributes: {[attr for attr in dir(kernel.agent_executor) if not attr.startswith('_')]}")
    else:
        print("\n3. Agent executor is None - failed to create")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_loaded_tools()
