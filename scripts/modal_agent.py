"""
Modal.com Integration for PocketAgent - Simplified Version

Usage:
    modal run modal_agent.py       # Test locally
    modal deploy modal_agent.py    # Deploy to cloud
"""

import modal

# Create the Modal app
app = modal.App("pocket-agent")

# Simple image for fast startup
agent_image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "openai",
    "httpx", 
    "fastapi[standard]",
)


# ============================================
# Simple Health Check (no secrets needed)
# ============================================

@app.function(image=agent_image)
@modal.web_endpoint(method="GET")
def health() -> dict:
    """Health check endpoint - no auth needed."""
    return {
        "status": "healthy",
        "service": "pocket-agent-modal",
        "message": "Modal Agent is running! 🚀"
    }


# ============================================
# LLM Endpoint (uses OpenRouter)
# ============================================

@app.function(
    image=agent_image,
    secrets=[modal.Secret.from_name("openrouter-api-key")],
    timeout=120,
)
@modal.web_endpoint(method="POST")
def ask(request: dict) -> dict:
    """
    Simple LLM endpoint using OpenRouter.
    
    POST /ask
    {"question": "What is the capital of France?"}
    """
    import os
    from openai import OpenAI
    
    question = request.get("question", "Hello!")
    
    try:
        client = OpenAI(
            api_key=os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1",
        )
        
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
            max_tokens=500,
        )
        
        answer = response.choices[0].message.content
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "model": "gpt-4o-mini"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ============================================
# Execute with Composio Tools
# ============================================

# Full image with Composio
full_image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "composio-langchain>=0.5,<0.6",
    "langchain",
    "langchain-openai",
    "openai",
    "httpx",
    "fastapi[standard]",
)


@app.function(
    image=full_image,
    secrets=[
        modal.Secret.from_name("openrouter-api-key"),
        modal.Secret.from_name("composio-secret"),
    ],
    timeout=300,
)
@modal.web_endpoint(method="POST")
def execute_task(request: dict) -> dict:
    """
    Execute a task with Composio tools.
    
    POST /execute_task
    {
        "goal": "Create a GitHub issue about the login bug",
        "apps": ["github"]
    }
    """
    import os
    import time
    from langchain_openai import ChatOpenAI
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from composio_langchain import ComposioToolSet, App
    
    goal = request.get("goal", "")
    apps = request.get("apps", [])
    
    if not goal:
        return {"error": "Missing 'goal' field"}
    
    start_time = time.time()
    
    try:
        # Initialize LLM
        llm = ChatOpenAI(
            model="openai/gpt-4o",
            openai_api_key=os.environ.get("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7,
        )
        
        # Initialize Composio
        composio = ComposioToolSet(api_key=os.environ.get("COMPOSIO_API_KEY"))
        
        # Get tools for requested apps
        if apps:
            app_enums = []
            for app_name in apps:
                try:
                    app_enum = getattr(App, app_name.upper().replace('-', '_'))
                    app_enums.append(app_enum)
                except AttributeError:
                    pass
            
            if app_enums:
                tools = composio.get_tools(apps=app_enums)
            else:
                tools = []
        else:
            tools = []
        
        if tools:
            # Create agent with tools
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful AI agent. Execute the user's request using available tools."),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            agent = create_openai_tools_agent(llm, tools, prompt)
            executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
            response = executor.invoke({"input": goal})
            result = response.get("output", str(response))
        else:
            # No tools - just use LLM
            response = llm.invoke(goal)
            result = response.content
        
        return {
            "success": True,
            "goal": goal,
            "result": result,
            "apps_used": apps,
            "execution_time": f"{time.time() - start_time:.2f}s"
        }
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


# ============================================
# List Composio Apps
# ============================================

@app.function(
    image=full_image,
    secrets=[modal.Secret.from_name("composio-secret")],
    timeout=60,
)
@modal.web_endpoint(method="GET")
def list_apps() -> dict:
    """List all available Composio apps."""
    from composio_langchain import App
    
    apps = [attr for attr in dir(App) if not attr.startswith('_')]
    return {
        "total": len(apps),
        "popular": ["GITHUB", "GMAIL", "SLACK", "NOTION", "GOOGLECALENDAR", "GOOGLEDRIVE"],
        "all_apps": apps[:100],
    }


# ============================================
# Local Testing
# ============================================

@app.local_entrypoint()
def main():
    """Quick local test."""
    print("🧪 Testing Modal Agent...")
    
    # Test simple ask
    result = ask.remote({"question": "What is 2+2? Reply with just the number."})
    print(f"✅ Ask test: {result}")
    
    print("\n🎉 Modal Agent is working!")
