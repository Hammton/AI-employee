
import os
from dotenv import load_dotenv
from composio import Composio
from composio_langchain import LangchainProvider

load_dotenv()
api_key = os.getenv("COMPOSIO_API_KEY")

print("--- Testing Composio SDK String-based ---")
try:
    print("Initializing Composio...")
    # Initialize with strings
    client = Composio(api_key=api_key)
    
    # Get Entity
    print("Getting Entity...")
    entity = client.get_entity(id="default")
    
    # Get Tools (passing strings)
    print("Fetching GMAIL tools...")
    # Note: get_tools might need to return Langchain compatible tools
    # In the new SDK, maybe we use the provider to format them?
    
    # Check if entity.get_tools takes a 'format' or if we wrap them
    tools = entity.get_tools(apps=["gmail"])
    
    print(f"✅ Found {len(tools)} raw tools.")
    
    # Converting to Langchain format?
    # The 'LangchainProvider' might be needed here or in Composio init
    
    print("\n--- Trying with LangchainProvider ---")
    client_lc = Composio(api_key=api_key) 
    # Can we just ask for langchain tools?
    
    # Based on other SDKs (e.g. OpenAI), it's often:
    # composio = Composio(provider=OpenAIAgentsProvider())
    # tools = composio.get_tools(...)
    
    client_provider = Composio(
        api_key=api_key,
        # provider=LangchainProvider() # Let's see if this works
    )
    # The error before was ImportError. Now let's see if param is accepted.
    
    # get_tools might have 'provider' arg?
    # tools = entity.get_tools(apps=["gmail"], provider=LangchainProvider())
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
