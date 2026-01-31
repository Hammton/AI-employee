"""
Diagnostic script to check PocketAgent setup
"""

import os
import requests
import sys

def check_env_vars():
    """Check if required environment variables are set."""
    print("=" * 60)
    print("1️⃣ Checking Environment Variables")
    print("=" * 60)
    
    required_vars = ["OPENROUTER_API_KEY", "COMPOSIO_API_KEY"]
    optional_vars = ["WPP_BRIDGE_URL", "PORT"]
    
    all_good = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"   ✅ {var}: {'*' * 20} (set)")
        else:
            print(f"   ❌ {var}: NOT SET")
            all_good = False
    
    for var in optional_vars:
        value = os.environ.get(var)
        if value:
            print(f"   ℹ️  {var}: {value}")
        else:
            print(f"   ℹ️  {var}: Not set (using default)")
    
    return all_good

def check_pocketagent():
    """Check if PocketAgent is running."""
    print("\n" + "=" * 60)
    print("2️⃣ Checking PocketAgent (Port 8000)")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ PocketAgent is running!")
            return True
        else:
            print(f"   ⚠️  PocketAgent responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ PocketAgent is NOT running on port 8000")
        return False
    except Exception as e:
        print(f"   ❌ Error checking PocketAgent: {e}")
        return False

def check_wpp_bridge():
    """Check if WPP Bridge is running."""
    print("\n" + "=" * 60)
    print("3️⃣ Checking WPP Bridge (Port 3001)")
    print("=" * 60)
    
    try:
        response = requests.get("http://localhost:3001/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ WPP Bridge is running!")
            print(f"   📱 Ready: {data.get('ready', False)}")
            print(f"   📱 Connected: {data.get('connected', False)}")
            return data.get('ready', False)
        else:
            print(f"   ⚠️  WPP Bridge responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ WPP Bridge is NOT running on port 3001")
        print("   💡 Start it with: cd wpp-bridge && npm start")
        return False
    except Exception as e:
        print(f"   ❌ Error checking WPP Bridge: {e}")
        return False

def check_webhook():
    """Test the webhook endpoint."""
    print("\n" + "=" * 60)
    print("4️⃣ Testing Webhook Endpoint")
    print("=" * 60)
    
    try:
        test_payload = {
            "id": "test_msg_123",
            "from": "test@c.us",
            "body": "test",
            "type": "chat"
        }
        response = requests.post(
            "http://localhost:8000/whatsapp/incoming",
            json=test_payload,
            timeout=10
        )
        if response.status_code == 200:
            print("   ✅ Webhook endpoint is working!")
            print(f"   📝 Response: {response.json()}")
            return True
        else:
            print(f"   ⚠️  Webhook responded with status {response.status_code}")
            print(f"   📝 Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ❌ Webhook endpoint not found!")
        print("   💡 You might be running main.py instead of main_v2.py")
        print("   💡 WPP Bridge requires main_v2.py")
        return False
    except Exception as e:
        print(f"   ❌ Error testing webhook: {e}")
        return False

def main():
    print("\n🔍 PocketAgent Diagnostic Tool\n")
    
    env_ok = check_env_vars()
    pocketagent_ok = check_pocketagent()
    wpp_bridge_ok = check_wpp_bridge()
    webhook_ok = check_webhook()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    print(f"   Environment Variables: {'✅' if env_ok else '❌'}")
    print(f"   PocketAgent Running: {'✅' if pocketagent_ok else '❌'}")
    print(f"   WPP Bridge Running: {'✅' if wpp_bridge_ok else '❌'}")
    print(f"   Webhook Endpoint: {'✅' if webhook_ok else '❌'}")
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS")
    print("=" * 60)
    
    if not env_ok:
        print("   ⚠️  Set missing environment variables in .env file")
    
    if not pocketagent_ok:
        print("   ⚠️  Start PocketAgent: python main_v2.py")
    
    if not wpp_bridge_ok:
        print("   ⚠️  Start WPP Bridge: cd wpp-bridge && npm start")
    
    if pocketagent_ok and not webhook_ok:
        print("   ⚠️  You're running main.py but WPP Bridge needs main_v2.py")
        print("   💡 Stop current server and run: python main_v2.py")
    
    if env_ok and pocketagent_ok and wpp_bridge_ok and webhook_ok:
        print("   🎉 Everything looks good!")
        print("   📱 Send a WhatsApp message to test")
    
    print("\n" + "=" * 60)
    
    return env_ok and pocketagent_ok and wpp_bridge_ok and webhook_ok

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Diagnostic failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
