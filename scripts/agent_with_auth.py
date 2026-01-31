"""Agent with in-chat authentication support"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("AGENT WITH IN-CHAT AUTHENTICATION")
print("=" * 60)

# Your user ID
USER_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

# Initialize Composio
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

# Create session
session = composio.create(user_id=USER_ID)

# Get ALL tools including Composio management tools
# These tools handle authentication automatically
print("\nGetting tools (including auth management)...")
tools = session.tools()

print(f"✅ Got {len(tools)} tools")
print("\nAvailable tools:")
for i, tool in enumerate(tools, 1):
    tool_name = tool.get('function', {}).get('name', 'Unknown')
    print(f"  {i}. {tool_name}")

# Create LLM
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

# Create agent with system prompt that explains authentication
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are a helpful assistant with access to various tools.

When a user asks you to perform an action that requires authentication:
1. Use COMPOSIO_SEARCH_TOOLS to find the right tools
2. If authentication is needed, use COMPOSIO_MANAGE_CONNECTIONS to get a connection link
3. Share the link with the user and ask them to authenticate
4. Once they confirm, proceed with the requested action

Always be helpful and guide users through the authentication process."""
)

print("\n✅ Agent created with authentication support!")
print("\n" + "=" * 60)
print("TESTING AGENT")
print("=" * 60)

# Test query
query = "Check my latest 3 Gmail emails"

print(f"\nUser: {query}\n")
print("Agent response:")
print("-" * 60)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": query
    }]
})

print(result['messages'][-1].content)
print("-" * 60)
