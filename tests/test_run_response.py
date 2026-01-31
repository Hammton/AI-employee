from dotenv import load_dotenv
load_dotenv()
from kernel import AgentKernel

k = AgentKernel()
# Simulate adding the app manually as if /connect gmail was run
print("Adding Gmail...")
k.add_apps(["gmail"]) 

print("Running 'Connect to Gmail'...")
response = k.run("Connect to Gmail")
print(f"Response: {response}")
