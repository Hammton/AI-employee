"""
Test Composio v0.11.0+ with new API
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Testing Composio v0.11.0+ ===\n")

# Test 1: Basic Composio client
print("1. Testing Composio client...")
try:
    from composio import Composio
    
    api_key = os.getenv("COMPOSIO_API_KEY")
    print(f"   API Key: {api_key[:10]}...")
    
    composio = Composio(api_key=api_key)
    print("   ✅ Composio client created")
    
    # Check available methods
    methods = [x for x in dir(composio) if not x.startswith('_')]
    print(f"   Available methods: {methods[:5]}...")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: LangChain Provider
print("\n2. Testing LangchainProvider...")
try:
    from composio_langchain import LangchainProvider
    from composio import Composio
    
    composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
    provider = LangchainProvider(composio=composio)
    
    print("   ✅ LangchainProvider created")
    
    # Check available methods
    methods = [x for x in dir(provider) if not x.startswith('_')]
    print(f"   Available methods: {methods}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Get tools for a specific app
print("\n3. Testing tool retrieval...")
try:
    from composio_langchain import LangchainProvider
    from composio import Composio
    
    composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
    provider = LangchainProvider(composio=composio)
    
    # Try to get GMAIL tools
    # New API might use: provider.get_tools(apps=["gmail"])
    # or provider.get_tools(toolkits=["gmail"])
    
    print("   Attempting to get GMAIL tools...")
    
    # Try different methods
    if hasattr(provider, 'get_tools'):
        try:
            tools = provider.get_tools(apps=["gmail"])
            print(f"   ✅ Got {len(tools)} tools using apps=['gmail']")
            if tools:
                print(f"   First tool: {tools[0].name}")
        except Exception as e1:
            print(f"   ⚠️  apps=['gmail'] failed: {e1}")
            try:
                tools = provider.get_tools(toolkits=["gmail"])
                print(f"   ✅ Got {len(tools)} tools using toolkits=['gmail']")
                if tools:
                    print(f"   First tool: {tools[0].name}")
            except Exception as e2:
                print(f"   ⚠️  toolkits=['gmail'] failed: {e2}")
    else:
        print("   ❌ No get_tools method found")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
