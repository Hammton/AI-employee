"""Test Composio agent with OpenRouter - Full execution"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=== Setting up Composio Agent ===\n")

# Step 1: Initialize Composio
from composio import Composio

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id="user_123")
tools = session.tools()
print(f"✅ Got {len(tools)} Composio tools\n")

# Step 2: Setup OpenRouter LLM
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "google/gemini-flash-1.5"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)
print("✅ OpenRouter LLM configured\n")

# Step 3: Create agent
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant with access to various tools. Use them when needed."
)
print("✅ Agent created\n")

# Step 4: Test with a simple query
print("=== Testing Agent ===\n")
test_query = "What tools do you have access to? List the first 3."

print(f"Query: {test_query}\n")
print("Running agent...\n")

try:
    result = agent.invoke({"messages": [{"role": "user", "content": test_query}]})
    
    print("=== Agent Response ===")
    print(f"Full result keys: {result.keys()}\n")
    
    # Extract all messages
    messages = result.get("messages", [])
    print(f"Total messages: {len(messages)}\n")
    
    for i, msg in enumerate(messages):
        print(f"Message {i+1}:")
        if hasattr(msg, 'content'):
            print(f"  Role: {getattr(msg, 'role', 'unknown')}")
            print(f"  Content: {msg.content}")
        else:
            print(f"  {msg}")
        print()
    
    print("✅ Test completed successfully!")
    
except Exception as e:
    print(f"❌ Error during execution: {e}")
    import traceback
    traceback.print_exc()
