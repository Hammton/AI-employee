"""Test getting Asana projects without workspace ID"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def test_asana_projects():
    """Test getting all Asana projects"""
    print("\n" + "=" * 70)
    print("TESTING ASANA - GET ALL PROJECTS")
    print("=" * 70)
    
    # Use the entity with ACTIVE Asana connection
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    
    # Create kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["asana"])
    print("   ✓ Kernel initialized")
    
    # Check connection
    print("\n2. Checking Asana connection...")
    is_connected = kernel.check_connection("asana")
    print(f"   {'✓ CONNECTED' if is_connected else '✗ NOT CONNECTED'}")
    
    if not is_connected:
        print("\n   ERROR: Asana not connected!")
        return
    
    # Test getting projects
    print("\n3. Asking agent to get all projects...")
    print("-" * 70)
    
    try:
        # Try a more direct request
        result = kernel.run(
            "Get all my Asana projects. List every project you can find. "
            "If you need a workspace, try to find it first or use any available method."
        )
        
        print("-" * 70)
        print("\n4. RESULT:")
        print(result)
        
        # Check if it worked
        if "project" in result.lower() and ("cross" in result.lower() or "content" in result.lower()):
            print("\n   STATUS: ✓ SUCCESS - Found projects!")
        elif "workspace" in result.lower() and "need" in result.lower():
            print("\n   STATUS: ⚠ PARTIAL - Still needs workspace info")
        else:
            print("\n   STATUS: ⚠ UNKNOWN - Check result above")
            
    except Exception as e:
        print("-" * 70)
        print(f"\n4. ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_asana_projects()
