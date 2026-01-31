"""
Test Composio v0.11.0+ with correct new API pattern
Based on docs: composio.create() returns a session with tools
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Testing Composio v0.11.0+ New Pattern ===\n")

try:
    from composio import Composio
    from composio_langchain import LangchainProvider
    
    api_key = os.getenv("COMPOSIO_API_KEY")
    print(f"API Key: {api_key[:10]}...")
    
    # Step 1: Create Composio client
    composio = Composio(api_key=api_key)
    print("✅ Composio client created\n")
    
    # Step 2: Create a session for a user
    user_id = "test_user_123"
    print(f"Creating session for user: {user_id}")
    
    # According to docs: session = composio.create(user_id=...)
    session = composio.create(user_id=user_id)
    print(f"✅ Session created: {type(session)}")
    print(f"   Session methods: {[x for x in dir(session) if not x.startswith('_')]}\n")
    
    # Step 3: Get tools from session
    print("Getting tools from session...")
    
    # Try different methods to get tools
    if hasattr(session, 'tools'):
        tools = session.tools(toolkits=["gmail"])
        print(f"✅ Got {len(tools)} tools using session.tools()")
        if tools:
            print(f"   Sample tools:")
            for tool in tools[:3]:
                print(f"   - {tool}")
    elif hasattr(session, 'get_tools'):
        tools = session.get_tools(apps=["gmail"])
        print(f"✅ Got {len(tools)} tools using session.get_tools()")
    else:
        print("❌ No tools method found on session")
        print(f"   Available: {[x for x in dir(session) if not x.startswith('_')]}")
    
    # Step 4: Try LangchainProvider with session
    print("\nTrying LangchainProvider...")
    provider = LangchainProvider(composio=composio)
    
    # Check if we can wrap tools
    if hasattr(provider, 'wrap_tools'):
        print("✅ Provider has wrap_tools method")
        # Try to wrap the tools we got
        if 'tools' in locals():
            wrapped = provider.wrap_tools(tools)
            print(f"   Wrapped {len(wrapped)} tools for LangChain")
            if wrapped:
                print(f"   First wrapped tool: {wrapped[0].name}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Test Complete ===")
