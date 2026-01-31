"""
Interactive Tool Testing - Step by Step
Guides you through authenticating and testing each tool
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

from kernel import AgentKernel

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text):
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print(f"{'─' * 80}")

def wait_for_user():
    input("\n👉 Press Enter to continue...")

# Initialize
print_header("🚀 INTERACTIVE MULTI-TOOL TEST")
print("\nThis script will guide you through:")
print("  1. Authenticating each tool")
print("  2. Testing basic functionality")
print("  3. Running example queries")

wait_for_user()

# Create kernel
user_id = "interactive_test_user"
print_section(f"Creating Kernel for user: {user_id}")
kernel = AgentKernel(user_id=user_id)
print("✅ Kernel created successfully!")

# Tools configuration
tools = [
    {
        "slug": "googlesheets",
        "name": "Google Sheets",
        "emoji": "📊",
        "test_query": "List my Google Sheets spreadsheets",
        "example": "Create a new spreadsheet called 'Test Sheet'"
    },
    {
        "slug": "googledocs",
        "name": "Google Docs",
        "emoji": "📝",
        "test_query": "List my recent Google Docs",
        "example": "Create a new document called 'Meeting Notes'"
    },
    {
        "slug": "notion",
        "name": "Notion",
        "emoji": "📓",
        "test_query": "List my Notion pages",
        "example": "Create a new page called 'Project Ideas'"
    },
    {
        "slug": "github",
        "name": "GitHub",
        "emoji": "🐙",
        "test_query": "List my GitHub repositories",
        "example": "Show me open issues in my repositories"
    },
    {
        "slug": "slack",
        "name": "Slack",
        "emoji": "💬",
        "test_query": "List my Slack channels",
        "example": "Send a message to #general saying 'Hello from AI!'"
    }
]

# Test each tool
for i, tool in enumerate(tools, 1):
    print_header(f"{tool['emoji']} TOOL {i}/{len(tools)}: {tool['name']}")
    
    # Step 1: Get auth URL
    print(f"\n📍 Step 1: Authentication")
    print(f"   Getting authentication URL for {tool['name']}...")
    
    try:
        auth_url = kernel.get_auth_url(tool['slug'])
        
        if "already connected" in auth_url.lower():
            print(f"   ✅ {auth_url}")
            is_connected = True
        else:
            print(f"\n   🔗 Authentication URL:")
            print(f"   {auth_url}")
            print(f"\n   👉 Please:")
            print(f"      1. Copy the URL above")
            print(f"      2. Open it in your browser")
            print(f"      3. Complete the OAuth flow")
            print(f"      4. Come back here")
            
            wait_for_user()
            is_connected = False
    except Exception as e:
        print(f"   ❌ Error getting auth URL: {e}")
        continue
    
    # Step 2: Setup toolkit
    print(f"\n📍 Step 2: Setup Toolkit")
    print(f"   Adding {tool['name']} to kernel...")
    
    try:
        kernel.setup(apps=[tool['slug'].upper()])
        print(f"   ✅ Toolkit added! Active: {kernel.active_apps}")
    except Exception as e:
        print(f"   ❌ Setup error: {e}")
        continue
    
    # Step 3: Test query
    print(f"\n📍 Step 3: Test Query")
    print(f"   Query: '{tool['test_query']}'")
    
    if not is_connected:
        print(f"\n   ⚠️  Skipping test (not authenticated yet)")
        print(f"      Run this script again after authenticating!")
    else:
        try:
            print(f"   🤔 Thinking...")
            response = kernel.run(tool['test_query'])
            
            # Display response
            if len(response) > 400:
                print(f"\n   ✅ Response (truncated):")
                print(f"   {response[:400]}...")
            else:
                print(f"\n   ✅ Response:")
                print(f"   {response}")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            print(f"      This might mean authentication is needed or expired")
    
    # Step 4: Example usage
    print(f"\n📍 Step 4: Example Usage")
    print(f"   Try this query: '{tool['example']}'")
    
    if i < len(tools):
        print(f"\n{'─' * 80}")
        print(f"  Moving to next tool...")
        wait_for_user()

# Final summary
print_header("🎉 ALL TOOLS TESTED!")

print("\n📊 Summary:")
print(f"   • User ID: {user_id}")
print(f"   • Active Toolkits: {len(kernel.active_apps)}")
print(f"   • Toolkits: {', '.join(kernel.active_apps)}")

print("\n💡 What You Can Do Now:")
print("\n   1. Single Tool Queries:")
for tool in tools:
    print(f"      {tool['emoji']} {tool['example']}")

print("\n   2. Multi-Tool Workflows:")
print("      📊➡️📓 'Export my Google Sheet to a Notion page'")
print("      🐙➡️💬 'Share my latest GitHub commits in Slack'")
print("      📝➡️📊 'Create a spreadsheet from my Google Doc'")

print("\n   3. Complex Automation:")
print("      'Every day, create a Notion page with my GitHub activity")
print("       and share it in Slack #dev-updates'")

print("\n🔧 Custom Test:")
print("   Want to try a custom query? Run:")
print("   >>> from kernel import AgentKernel")
print(f"   >>> kernel = AgentKernel(user_id='{user_id}')")
print("   >>> kernel.setup(apps=['GITHUB', 'SLACK', 'NOTION'])")
print("   >>> kernel.run('your query here')")

print("\n" + "=" * 80)
print("  🚀 Happy Automating!")
print("=" * 80 + "\n")
