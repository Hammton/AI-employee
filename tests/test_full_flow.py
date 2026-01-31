from dotenv import load_dotenv
load_dotenv()
from kernel import AgentKernel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Test")

print("Initializing Kernel...")
k = AgentKernel()

print("\n--- Testing Setup and Tool Loading ---")
# This should trigger setup()
k.setup(apps=["gmail"])
print(f"Active Apps: {k.active_apps}")
print(f"Agent Executor Initialized: {k.agent_executor is not None}")

if k.agent_executor:
    print(f"Tools count: {len(k.agent_executor.tools)}")
    for t in k.agent_executor.tools[:5]:
        print(f" - Tool: {t.name}")

print("\n--- Testing Agent Run (Simple) ---")
try:
    response = k.run("Hello, who are you?")
    print(f"Response: {response}")
except Exception as e:
    print(f"Run Error: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Testing Connect Command Logic (Simulation) ---")
try:
    url = k.get_auth_url("github")
    print(f"Auth URL: {url}")
except Exception as e:
    print(f"Auth Error: {e}")
