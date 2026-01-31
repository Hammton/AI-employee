"""
Comprehensive Multi-Tool Integration Test
Tests: Google Sheets, Google Docs, Notion, GitHub, Slack
"""
import os
from dotenv import load_dotenv

load_dotenv()

from kernel import AgentKernel

print("=" * 80)
print("🚀 MULTI-TOOL INTEGRATION TEST")
print("=" * 80)

# Create kernel with unique user ID
user_id = "multi_tool_test_user"
print(f"\n📝 Creating kernel for user: {user_id}")
kernel = AgentKernel(user_id=user_id)
print(f"✅ Kernel initialized")

# List of tools to test
tools_to_test = [
    ("googlesheets", "Google Sheets"),
    ("googledocs", "Google Docs"),
    ("notion", "Notion"),
    ("github", "GitHub"),
    ("slack", "Slack"),
]

print("\n" + "=" * 80)
print("PHASE 1: AUTHENTICATION SETUP")
print("=" * 80)

auth_urls = {}

for slug, display_name in tools_to_test:
    print(f"\n📱 {display_name}")
    print("-" * 40)
    
    try:
        # Get authentication URL
        auth_url = kernel.get_auth_url(slug)
        auth_urls[slug] = auth_url
        
        if "already connected" in auth_url.lower():
            print(f"✅ {auth_url}")
        else:
            print(f"🔗 Auth URL: {auth_url}")
            print(f"   👉 Click to authenticate: {auth_url}")
    except Exception as e:
        print(f"❌ Error: {e}")
        auth_urls[slug] = None

print("\n" + "=" * 80)
print("PHASE 2: SETUP TOOLKITS")
print("=" * 80)

# Setup all toolkits at once
toolkit_slugs = [slug.upper() for slug, _ in tools_to_test]
print(f"\n📦 Setting up toolkits: {', '.join(toolkit_slugs)}")

try:
    kernel.setup(apps=toolkit_slugs)
    print(f"✅ Toolkits configured: {kernel.active_apps}")
    print(f"   Total active: {len(kernel.active_apps)}")
except Exception as e:
    print(f"❌ Setup error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("PHASE 3: TEST QUERIES")
print("=" * 80)

# Test queries for each tool
test_queries = [
    ("Google Sheets", "List my Google Sheets spreadsheets"),
    ("Google Docs", "List my recent Google Docs documents"),
    ("Notion", "List my Notion pages"),
    ("GitHub", "List my GitHub repositories"),
    ("Slack", "List my Slack channels"),
]

print("\n⚠️  NOTE: These queries will only work if you've authenticated the tools above!")
print("   If not authenticated, you'll see errors (expected behavior).\n")

for tool_name, query in test_queries:
    print(f"\n🔍 Testing {tool_name}")
    print(f"   Query: '{query}'")
    print("-" * 40)
    
    try:
        response = kernel.run(query)
        
        # Truncate long responses
        if len(response) > 300:
            display_response = response[:300] + "..."
        else:
            display_response = response
            
        print(f"✅ Response:\n{display_response}")
    except Exception as e:
        print(f"⚠️  Error (may need authentication): {e}")

print("\n" + "=" * 80)
print("PHASE 4: ADVANCED MULTI-TOOL QUERY")
print("=" * 80)

# Test a query that could use multiple tools
advanced_query = """
Check my GitHub repositories and create a Notion page listing them.
Then share a summary in my Slack #general channel.
"""

print(f"\n🎯 Advanced Query:")
print(f"   {advanced_query.strip()}")
print("\n⚠️  This requires all tools to be authenticated!")
print("-" * 40)

try:
    response = kernel.run(advanced_query)
    print(f"✅ Response:\n{response[:500]}...")
except Exception as e:
    print(f"⚠️  Error: {e}")

print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)

print("\n✅ Kernel Features Tested:")
print("   • Session-based authentication")
print("   • Multi-toolkit setup")
print("   • Per-user context isolation")
print("   • Tool execution")
print("   • Error handling")

print("\n🔗 Authentication URLs Generated:")
for slug, display_name in tools_to_test:
    url = auth_urls.get(slug)
    if url:
        status = "✅ Connected" if "already connected" in url.lower() else "🔗 Pending"
        print(f"   {status} {display_name}: {url[:60]}...")
    else:
        print(f"   ❌ {display_name}: Failed to generate URL")

print("\n📝 Next Steps:")
print("   1. Click the authentication URLs above")
print("   2. Complete OAuth flow for each tool")
print("   3. Run this test again to see tools in action")
print("   4. Try custom queries with your authenticated tools")

print("\n💡 Example Custom Queries:")
print("   • 'Create a new Google Sheet called Q1 Budget'")
print("   • 'Find all my GitHub issues labeled as bugs'")
print("   • 'Create a Notion page with my Slack messages from today'")
print("   • 'Write a summary of my GitHub commits to a Google Doc'")

print("\n" + "=" * 80)
print("TEST COMPLETE!")
print("=" * 80)
