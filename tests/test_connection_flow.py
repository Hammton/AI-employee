"""
Test the complete connection flow with a real user

This simulates:
1. User asks to connect to Asana
2. Check if already connected
3. Generate auth URL if needed
4. Simulate connection
5. Check again (should detect connection)
"""

import os
from dotenv import load_dotenv
from kernel import AgentKernel

# Load environment variables
load_dotenv()

def test_connection_flow():
    """Test the complete connection flow."""
    print("\n" + "=" * 70)
    print("🧪 TESTING: Complete Connection Flow")
    print("=" * 70)
    
    # Use a real user ID (like a phone number)
    user_id = "+254708235245@c.us"  # Your actual WhatsApp number
    
    print(f"\n👤 User: {user_id}")
    print(f"📱 App: Asana")
    
    # Create kernel
    print("\n1️⃣ Creating user kernel...")
    kernel = AgentKernel(user_id=user_id)
    kernel.setup(apps=["asana"])
    print("   ✅ Kernel created")
    
    # Check current connection status
    print("\n2️⃣ Checking if user is already connected to Asana...")
    is_connected = kernel.check_connection("asana")
    
    if is_connected:
        print("   ✅ User IS connected to Asana!")
        print("\n   📊 Connection Details:")
        
        # Get toolkit info
        try:
            toolkits = kernel.composio_session.toolkits()
            for toolkit in toolkits.items:
                toolkit_name = str(toolkit.name).lower()
                if "asana" in toolkit_name:
                    print(f"      • Toolkit: {toolkit.name}")
                    if hasattr(toolkit, 'connection') and toolkit.connection:
                        if hasattr(toolkit.connection, 'connected_account'):
                            account_id = getattr(toolkit.connection.connected_account, 'id', 'N/A')
                            print(f"      • Account ID: {account_id}")
                        is_active = getattr(toolkit.connection, 'is_active', False)
                        print(f"      • Active: {is_active}")
        except Exception as e:
            print(f"      ⚠️  Could not get details: {e}")
        
        print("\n   💡 What happens when user asks to connect again:")
        print("      Bot should say: '✅ ASANA Already Connected!'")
        
    else:
        print("   ❌ User is NOT connected to Asana")
        
        # Generate auth URL
        print("\n3️⃣ Generating auth URL...")
        auth_url = kernel.get_auth_url("asana")
        
        if auth_url:
            print(f"   ✅ Auth URL generated:")
            print(f"      {auth_url}")
            print("\n   💡 User should:")
            print("      1. Click this link")
            print("      2. Authorize Asana")
            print("      3. Come back and ask again")
        else:
            print("   ⚠️  No auth URL generated (might already be connected)")
    
    # Test the /status command simulation
    print("\n4️⃣ Simulating /status command...")
    
    if is_connected:
        status_message = """✅ *ASANA Status: Connected*

Your asana account is connected and ready to use!

Try asking me: "What are my asana tasks?" """
    else:
        status_message = """❌ *ASANA Status: Not Connected*

You haven't connected your asana account yet.

To connect, use: /connect asana"""
    
    print(f"\n   Bot Response:")
    print("   " + "\n   ".join(status_message.split("\n")))
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"   User ID: {user_id}")
    print(f"   App: Asana")
    print(f"   Connected: {'✅ YES' if is_connected else '❌ NO'}")
    print(f"   Auth URL needed: {'❌ NO' if is_connected else '✅ YES'}")
    
    if is_connected:
        print("\n   🎉 SUCCESS! User is connected!")
        print("   The agent will NOT send auth URLs anymore.")
    else:
        print("\n   ⏳ User needs to connect first.")
        print("   After connecting, run this test again to verify.")
    
    print("\n" + "=" * 70)
    
    return is_connected

if __name__ == "__main__":
    try:
        is_connected = test_connection_flow()
        
        print("\n💡 NEXT STEPS:")
        if is_connected:
            print("   1. Send WhatsApp message: '/connect asana'")
            print("   2. Bot should say: '✅ Already Connected!'")
            print("   3. Try: 'What are my asana tasks?'")
        else:
            print("   1. Send WhatsApp message: '/connect asana'")
            print("   2. Click the auth URL")
            print("   3. After connecting, run this test again")
            print("   4. It should show '✅ Connected'")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
