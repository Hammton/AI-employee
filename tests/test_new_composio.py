
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
print(f"Testing new Composio SDK with key: {api_key[:5]}...")

try:
    composio_client = Composio(api_key=api_key)
    print("Instance created.")
    
    # Create a session or get user
    user_id = "default_user_2"
    print(f"Creating session for {user_id}...")
    
    # Based on user docs, session = composio.create(...)
    # Note: verify if it returns an object with .tools()
    session = composio_client.get_entity(id=user_id) 
    # Or maybe composio.create is for sessions? 
    # Let's inspect the object
    print(f"Session object: {session}")
    
    print("Fetching GMAIL tools from entity...")
    # New SDK might use different method
    # user doc says: tools = session.tools() or similar?
    # The doc says: session = composio.create(user_id=...); tools = session.tools()
    
    # Let's try to follow the doc provided exactly if possible, but I suspect 'composio.create' might imply 'composio.users.create' or similar in earlier versions, 
    # but let's try exactly what user pasted:
    # session = composio.create(user_id=...)
    
    if hasattr(composio_client, 'create'):
         session = composio_client.create(user_id=user_id)
         print("Called composio.create()")
    else:
         print("composio.create not found, using get_entity")
         session = composio_client.get_entity(id=user_id)

    # Now let's try to get tools
    # Using the Langchain integration if available, OR just raw tools
    # The user is using 'composio_openai_agents' in their example, but we are using Langchain.
    # We need to bridge this back to Langchain.
    
    # Check if we can get tools for Langchain
    from composio_langchain import ComposioToolSet, App
    toolset = ComposioToolSet(api_key=api_key)
    tools = toolset.get_tools(apps=[App.GMAIL])
    print(f"✅ Langchain Tools: {len(tools)}")
    print(f"Sample: {tools[0].name}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
