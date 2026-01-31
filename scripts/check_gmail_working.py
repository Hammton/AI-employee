"""Check Gmail - Using the working pattern from earlier"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 60)
print("CHECKING GMAIL EMAILS")
print("=" * 60)

# Use your actual entity ID where Gmail is connected
USER_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

# Setup
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=USER_ID)
tools = session.tools()

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are a helpful email assistant. 

When asked to check emails:
1. Use COMPOSIO_SEARCH_TOOLS to find Gmail tools
2. Use the appropriate Gmail tool to fetch emails
3. Summarize the results for the user

Be helpful and clear in your responses."""
)

print(f"\nOK Setup complete!")
print(f"   - User ID: {USER_ID}")
print(f"   - Tools: {len(tools)}")
print(f"   - Model: {os.getenv('LLM_MODEL')}\n")

print("=" * 60)
print("ASKING AGENT TO CHECK EMAILS")
print("=" * 60)

# Ask to check emails
query = "Please check my latest 3 Gmail emails and tell me who they're from and what they're about."

print(f"\nUser: {query}\n")
print("Agent working...")
print("-" * 60)

result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": query
    }]
})

print("\n" + "=" * 60)
print("AGENT RESPONSE:")
print("=" * 60)
print(f"\n{result['messages'][-1].content}\n")
print("=" * 60)
