
import os
from dotenv import load_dotenv
from composio_langchain import ComposioToolSet, App
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Load env vars
load_dotenv()

# Setup Composio
api_key = os.getenv("COMPOSIO_API_KEY")
print(f"Using Composio Key: {api_key[:5]}...")

toolset = ComposioToolSet(api_key=api_key)

try:
    # Get Gmail tools
    print("Getting Gmail tools...")
    tools = toolset.get_tools(apps=[App.GMAIL])
    print(f"✅ Found {len(tools)} Gmail tools.")
    
    # Initialize LLM
    llm = ChatOpenAI(
        model="openai/gpt-4o", 
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1"
    )

    # Create Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant."),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    # Execute
    print("\n🚀 Executing Agent Task: 'Get the latest email regarding AI automation'")
    result = agent_executor.invoke({"input": "Get the latest email regarding AI automation"})
    print("\n✅ Result:", result['output'])

except Exception as e:
    print(f"\n❌ Error: {e}")
