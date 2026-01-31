"""Simple test without tools first"""
import os
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0
)

print("Testing LLM without tools...")
response = llm.invoke("Say 'Hello, I am working!' in one sentence.")
print(f"Response: {response.content}")
print("\n✅ LLM works!\n")

# Now test with Composio tools
print("Testing with Composio tools...")
from composio import Composio
from langchain.agents import create_agent

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id="user_123")
tools = session.tools()

print(f"Tools type: {type(tools)}")
print(f"First tool type: {type(tools[0])}")
print(f"First tool keys: {tools[0].keys() if isinstance(tools[0], dict) else 'not a dict'}\n")

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant."
)

result = agent.invoke({"messages": [{"role": "user", "content": "Just say hello"}]})
print(f"Agent response: {result['messages'][-1].content}")
