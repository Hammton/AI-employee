"""Working Composio v0.11.0+ example with OpenRouter"""
import os
from dotenv import load_dotenv

load_dotenv()

from composio import Composio
from composio_langchain import LangchainProvider

# Initialize
composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id="user_123")

# Get all tools
tools = session.tools()
print(f"✅ Got {len(tools)} tools")

# Wrap for LangChain - tools are already executable
langchain_tools = tools
print(f"✅ Wrapped {len(langchain_tools)} tools for LangChain")
print(f"Sample: {langchain_tools[0]}")

# Use with OpenRouter + LangChain
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

llm = ChatOpenAI(
    model="google/gemini-2.0-flash-exp:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

agent = create_agent(
    model=llm,
    tools=langchain_tools[:5],  # Use first 5 tools
    system_prompt="You are a helpful assistant with access to various tools."
)

print("✅ Agent created successfully!")
