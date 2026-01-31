"""Downgrade to Composio v0.5.51 which has the old working API"""
import subprocess
import sys

print("Downgrading Composio to v0.5.51 (working version)...\n")

try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", 
         "composio-core==0.5.51", 
         "composio-langchain==0.5.51"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Successfully downgraded to v0.5.51")
        print("\nNow you can use the old API:")
        print("  from composio_langchain import ComposioToolSet, App")
        print("  toolset = ComposioToolSet()")
        print("  tools = toolset.get_tools(apps=[App.GMAIL])")
    else:
        print(f"❌ Error: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
