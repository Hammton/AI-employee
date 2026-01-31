"""
PocketAgent Cloud Deployment (Modal.com)
Matches MoltBot/ClawdBot infrastructure using Hosted Browser.

Deploys the EXACT kernel.py logic we fixed (BatchOperation, Auth) to the cloud.
"""

import modal
import os

# Define image with same requirements as local
image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "composio-core==0.5.51",
        "composio-langchain==0.5.51",
        "langchain",
        "langchain-openai",
        "openai",
        "fastapi",
        "uvicorn",
        "python-multipart",
        "httpx",
        "qrcode",
        "pillow",
        "python-dotenv",
        "pypdf",
        "python-docx",
        "pydantic"
    )
    .env({"COMPOSIO_LOG_LEVEL": "INFO"})
)

app = modal.App("pocket-agent-v2")

@app.cls(
    image=image,
    secrets=[
        modal.Secret.from_name("openrouter-api-key"),
        modal.Secret.from_name("composio-secret"), # Ensure this exists in Modal dashboard
    ],
    mounts=[modal.Mount.from_local_file("kernel.py", remote_path="/root/kernel.py")],
    timeout=600  # 10 minutes for complex browser tasks
)
class CloudAgent:
    def __init__(self):
        # Import inside container
        from kernel import AgentKernel
        self.kernel = AgentKernel()
        
    @modal.enter()
    def setup(self):
        """Initialize kernel with standard tools + Browser"""
        print("Initializing Cloud Agent...")
        # Add basic apps + ANCHOR_BROWSER for web capabilities
        self.kernel.setup(apps=["GMAIL", "GOOGLECALENDAR", "NOTION", "ANCHOR_BROWSER"])
        print("Cloud Agent Ready.")

    @modal.web_endpoint(method="POST")
    def webhook(self, item: dict):
        """
        Webhook for WhatsApp/External triggers.
        POST {"goal": "Create a summary of moltbot.org"}
        """
        goal = item.get("goal")
        if not goal:
            return {"error": "No goal provided"}
            
        print(f"Received goal: {goal}")
        result = self.kernel.run(goal)
        return {"response": result}

    @modal.method()
    def background_run(self, goal: str):
        """Async execution method"""
        return self.kernel.run(goal)

# Local test entrypoint
@app.local_entrypoint()
def main():
    print("🚀 Deploying local test to cloud...")
    agent = CloudAgent()
    
    # Test browser capability
    goal = "Go to moltbot.org and summarize what it does."
    print(f"Sending goal: {goal}")
    
    response = agent.background_run.remote(goal)
    print(f"Response: {response}")
