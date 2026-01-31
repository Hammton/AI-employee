"""Check what Asana tools are actually loaded in the kernel"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def check_kernel_tools():
    """Check what tools the kernel actually loads"""
    print("\n" + "=" * 70)
    print("CHECKING KERNEL ASANA TOOLS")
    print("=" * 70)
    
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    
    # Create kernel
    print("\n1. Initializing kernel with Asana...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["asana"])
    print("   ✓ Kernel initialized")
    
    # Check what tools are available
    print("\n2. Checking loaded tools...")
    
    if hasattr(kernel, 'tools') and kernel.tools:
        print(f"\n   Found {len(kernel.tools)} tools total\n")
        
        asana_tools = [t for t in kernel.tools if 'ASANA' in str(t.name if hasattr(t, 'name') else t)]
        print(f"   Asana tools: {len(asana_tools)}\n")
        
        for tool in asana_tools:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            print(f"   - {tool_name}")
    else:
        print("   ✗ No tools found!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_kernel_tools()
