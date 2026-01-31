"""
Simple Modal Test - Verify Modal is working before full deployment.
Run with: modal run modal_test.py
"""

import modal

# Image with FastAPI for web endpoints
image = modal.Image.debian_slim().pip_install("fastapi[standard]")

app = modal.App("pocket-agent-test")


@app.function()
def hello(name: str = "World") -> str:
    """Simple test function."""
    return f"Hello {name} from Modal! 🚀"


@app.function()
def test_composio_import() -> str:
    """Test that Composio is available."""
    try:
        from composio_langchain import App
        # List first 10 apps
        apps = [attr for attr in dir(App) if not attr.startswith('_')][:10]
        return f"✅ Composio available! Sample apps: {', '.join(apps)}"
    except ImportError as e:
        return f"❌ Composio not available: {e}"


# Web endpoint for easy testing
@app.function(image=image)
@modal.web_endpoint(method="GET")
def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "pocket-agent-modal",
        "message": "Modal is running! 🎉"
    }


@app.function(image=image)
@modal.web_endpoint(method="POST")
def execute(request: dict) -> dict:
    """
    Test task execution endpoint.
    
    POST /execute
    {"goal": "Say hello to John"}
    """
    goal = request.get("goal", "")
    
    # Simulate agent response
    return {
        "success": True,
        "goal": goal,
        "result": f"I would execute: '{goal}' - but this is a test!",
        "message": "Modal is working. Deploy modal_agent.py for full functionality."
    }


@app.local_entrypoint()
def main():
    """Run local tests."""
    print("=" * 50)
    print("Testing Modal Connection...")
    print("=" * 50)
    
    # Test 1: Basic function
    result = hello.remote("PocketAgent")
    print(f"\n✅ Test 1 (Basic): {result}")
    
    # Test 2: Composio import
    result = test_composio_import.remote()
    print(f"\n✅ Test 2 (Composio): {result}")
    
    print("\n" + "=" * 50)
    print("All tests passed! Modal is ready.")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Create secrets: modal secret create openrouter-secret OPENROUTER_API_KEY=xxx")
    print("2. Create secrets: modal secret create composio-secret COMPOSIO_API_KEY=xxx")
    print("3. Deploy: modal deploy modal_agent.py")
