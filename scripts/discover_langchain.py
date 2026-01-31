
import pkgutil
import langchain.agents
import importlib

print("Searching for AgentExecutor in langchain.agents...")

if hasattr(langchain.agents, "AgentExecutor"):
    print("✅ Found langchain.agents.AgentExecutor")
else:
    print("❌ NOT Found in langchain.agents")
    # List available attributes
    print(f"Attributes: {[x for x in dir(langchain.agents) if not x.startswith('_')]}")

try:
    from langchain.agents import AgentExecutor
    print("✅ Successfully imported AgentExecutor from langchain.agents")
except ImportError as e:
    print(f"❌ Import failed: {e}")

try:
    from langchain.agents.agent import AgentExecutor
    print("✅ Successfully imported AgentExecutor from langchain.agents.agent")
except ImportError as e:
    print(f"❌ Import from langchain.agents.agent failed: {e}")

