
import os
import sys
from dotenv import load_dotenv

# Load env before imports
load_dotenv()

# Ensure current dir is in path
sys.path.append(os.getcwd())

from kernel import AgentKernel
from composio_langchain import App

print("Initializing Kernel...")
kernel = AgentKernel()

print("Connection Notion and Gmail...")
kernel.setup(apps=[App.GMAIL, App.NOTION])

print("\n🚀 Executing Agent Task: 'List my latest 3 emails (REAL TEST)'")
result = kernel.run("List my latest 3 emails. Provide sender and subject.")

print("\n✅ Result:\n")
print(result)
