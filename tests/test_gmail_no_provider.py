"""Test Gmail WITHOUT LangchainProvider - like the working example"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

print("=" * 70)
print("TESTING GMAIL WITHOUT LANGCHAINPROVIDER")
print("=" * 70)

# Use the user ID that has Gmail connected
USER_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"

print(f"\nUser: {USER_ID}")

# Setup WITHOUT LangchainProvider (like check_gmail_working.py)
print("\n1. Creating Composio client WITHOUT LangchainProvider...")
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=USER_ID)
tools = session.tools()

print(f"   OK Got {len(tools)} tools")
print(f"   Tool types: {[type(t) for t in tools[:2]]}")

# Setup LLM
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

print("\n2. Creating agent...")
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""You are a helpful email assistant. 

When asked to check emails:
1. Use COMPOSIO_SEARCH_TOOLS to find Gmail tools
2. Use the appropriate Gmail tool to fetch emails
3. Summarize the results for the user

CRITICAL: When calling COMPOSIO_SEARCH_TOOLS, use ONLY:
{"queries": [{"use_case": "your task"}]}
Do NOT include "session" parameter!

Be helpful and clear in your responses."""
)

print("   OK Agent created")

# Test query
print("\n3. Testing query...")
print("-" * 70)

query = "Please check my latest 3 Gmail emails and tell me who they're from and what they're about."

try:
    result = agent.invoke({
        "messages": [{
            "role": "user",
            "content": query
        }]
    })
    
    print("-" * 70)
    print("\n4. RESULT:")
    response = result['messages'][-1].content
    print(response)
    
    if "error" in response.lower() and "json" in response.lower():
        print("\n   STATUS: FAIL - JSON serialization error")
    elif "email" in response.lower() or "from" in response.lower():
        print("\n   STATUS: SUCCESS - Got Gmail data!")
    else:
        print("\n   STATUS: PARTIAL - Got response")
        
except Exception as e:
    print("-" * 70)
    print(f"\n4. ERROR: {e}")
    
    if "JSON serializable" in str(e):
        print("\n   STATUS: FAIL - Composio bug")
    else:
        print("\n   STATUS: FAIL - Different error")

print("\n" + "=" * 70)
