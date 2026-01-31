
import langchain.agents
print(f"Langchain Version: {langchain.__version__}")
print("Checking langchain.agents content:")
print([x for x in dir(langchain.agents) if not x.startswith("_")])

try:
    from langchain.agents import initialize_agent
    print("✅ initialize_agent found")
except ImportError:
    print("❌ initialize_agent NOT found")

try:
    from langchain.agents import create_openai_tools_agent
    print("✅ create_openai_tools_agent found")
except ImportError:
    print("❌ create_openai_tools_agent NOT found")

try:
    from langchain.agents import create_tool_calling_agent
    print("✅ create_tool_calling_agent found")
except ImportError:
    print("❌ create_tool_calling_agent NOT found")
