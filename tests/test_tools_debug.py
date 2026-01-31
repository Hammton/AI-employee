"""Debug what session.tools() returns"""
import os
from dotenv import load_dotenv
from composio import Composio

load_dotenv()

USER_ID = "+254708235245@c.us"

print("=" * 70)
print("DEBUGGING SESSION.TOOLS()")
print("=" * 70)

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))
session = composio.create(user_id=USER_ID)

print(f"\n✅ Session created for user: {USER_ID}")

# Get tools
tools = session.tools()

print(f"\n📦 Got {len(tools)} tools")
print(f"   Type: {type(tools)}")

if tools:
    print(f"\n🔍 First tool (dict):")
    first_tool = tools[0]
    print(f"   Type: {type(first_tool)}")
    
    if isinstance(first_tool, dict):
        print(f"   Keys: {list(first_tool.keys())}")
        for key, value in first_tool.items():
            if key != 'func':  # Skip function objects
                print(f"   {key}: {str(value)[:100]}")
    
    print(f"\n📋 All tools:")
    for i, tool in enumerate(tools, 1):
        if isinstance(tool, dict):
            func_info = tool.get('function', {})
            name = func_info.get('name', 'unknown')
            desc = func_info.get('description', '')[:80]
            print(f"   {i}. {name}")
            print(f"      {desc}...")

print("\n" + "=" * 70)
