"""Connect Anchor Browser to the agent"""
import os
from dotenv import load_dotenv
from kernel import AgentKernel

load_dotenv()

def connect_browser():
    """Generate auth link for Anchor Browser"""
    print("\n" + "=" * 70)
    print("CONNECTING ANCHOR BROWSER")
    print("=" * 70)
    
    # Use the WhatsApp user ID
    user_id = "+254708235245@c.us"
    print(f"\nUser: {user_id}")
    
    # Initialize kernel
    print("\n1. Initializing kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup()
    
    # Check if already connected
    print("\n2. Checking if Anchor Browser is already connected...")
    is_connected = kernel.check_connection("anchor_browser")
    print(f"   Connected: {is_connected}")
    
    if is_connected:
        print("\n   [OK] Anchor Browser is already connected!")
        print("   You can start using web browsing capabilities right away.")
    else:
        # Generate auth URL
        print("\n3. Generating authentication URL...")
        try:
            auth_url = kernel.get_auth_url("anchor_browser")
            print(f"\n   [AUTH URL]")
            print(f"   {auth_url}")
            print(f"\n   Please visit this URL to connect Anchor Browser.")
            print(f"   After connecting, the agent will have web browsing capabilities!")
        except Exception as e:
            print(f"\n   [ERROR] Failed to generate auth URL: {e}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    connect_browser()
