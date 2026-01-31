"""Final comprehensive test of Composio + OpenRouter + LangChain"""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("COMPOSIO + OPENROUTER + LANGCHAIN INTEGRATION TEST")
print("=" * 60)

# Setup
from composio import Composio
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id="test_user")
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
    system_prompt="You are a helpful assistant with access to various tools."
)

print(f"\n✅ Setup complete!")
print(f"   - Composio tools: {len(tools)}")
print(f"   - LLM model: {os.getenv('LLM_MODEL')}")
print(f"   - Agent: Ready\n")

# List available tools
print("Available Composio tools:")
for i, tool in enumerate(tools, 1):
    tool_name = tool.get('function', {}).get('name', 'Unknown')
    print(f"   {i}. {tool_name}")

print("\n" + "=" * 60)
print("RUNNING TEST QUERIES")
print("=" * 60)

# Test 1: Simple greeting
print("\n[Test 1] Simple greeting")
print("-" * 40)
result = agent.invoke({"messages": [{"role": "user", "content": "Hello! Introduce yourself briefly."}]})
print(f"Response: {result['messages'][-1].content}\n")

# Test 2: Ask about tools
print("[Test 2] Tool awareness")
print("-" * 40)
result = agent.invoke({"messages": [{"role": "user", "content": "What is the first tool you have access to? Just name it."}]})
print(f"Response: {result['messages'][-1].content}\n")

# Test 3: Simple task
print("[Test 3] Simple reasoning")
print("-" * 40)
result = agent.invoke({"messages": [{"role": "user", "content": "What is 25 * 4?"}]})
print(f"Response: {result['messages'][-1].content}\n")

print("=" * 60)
print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
print("\nYour Composio + OpenRouter + LangChain setup is working!")
