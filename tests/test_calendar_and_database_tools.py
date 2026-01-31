"""
Test Calendar & Database Tools: Cal.com, Calendly, Airtable
"""
import os
from dotenv import load_dotenv

load_dotenv()

from kernel import AgentKernel

print("=" * 80)
print("📅 CALENDAR & DATABASE TOOLS TEST")
print("=" * 80)

# Create kernel
user_id = "calendar_db_test_user"
print(f"\n📝 Creating kernel for user: {user_id}")
kernel = AgentKernel(user_id=user_id)
print(f"✅ Kernel initialized")

# Tools to test
tools_to_test = [
    {
        "slug": "calcom",
        "name": "Cal.com",
        "emoji": "📆",
        "description": "Open-source scheduling platform",
        "test_queries": [
            "List my Cal.com event types",
            "Show my upcoming Cal.com bookings",
            "Create a new 30-minute meeting type called 'Quick Chat'"
        ]
    },
    {
        "slug": "calendly",
        "name": "Calendly",
        "emoji": "📅",
        "description": "Scheduling automation platform",
        "test_queries": [
            "List my Calendly event types",
            "Show my scheduled Calendly events",
            "Get my Calendly availability"
        ]
    },
    {
        "slug": "airtable",
        "name": "Airtable",
        "emoji": "🗄️",
        "description": "Cloud collaboration database",
        "test_queries": [
            "List my Airtable bases",
            "Show tables in my main Airtable base",
            "Create a new record in my tasks table"
        ]
    }
]

print("\n" + "=" * 80)
print("PHASE 1: AUTHENTICATION")
print("=" * 80)

auth_urls = {}

for tool in tools_to_test:
    print(f"\n{tool['emoji']} {tool['name']}")
    print(f"   {tool['description']}")
    print("-" * 80)
    
    try:
        auth_url = kernel.get_auth_url(tool['slug'])
        auth_urls[tool['slug']] = auth_url
        
        if "already connected" in auth_url.lower():
            print(f"   ✅ {auth_url}")
        else:
            print(f"   🔗 Auth URL: {auth_url}")
            print(f"   👉 Click to connect: {auth_url}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        auth_urls[tool['slug']] = None

print("\n" + "=" * 80)
print("PHASE 2: SETUP TOOLKITS")
print("=" * 80)

toolkit_slugs = [tool['slug'].upper() for tool in tools_to_test]
print(f"\n📦 Setting up: {', '.join(toolkit_slugs)}")

try:
    kernel.setup(apps=toolkit_slugs)
    print(f"✅ Configured: {kernel.active_apps}")
except Exception as e:
    print(f"❌ Setup error: {e}")

print("\n" + "=" * 80)
print("PHASE 3: TEST QUERIES")
print("=" * 80)

print("\n⚠️  NOTE: Queries will only work after authentication!\n")

for tool in tools_to_test:
    print(f"\n{tool['emoji']} {tool['name']} - Test Queries")
    print("=" * 80)
    
    for i, query in enumerate(tool['test_queries'], 1):
        print(f"\n   {i}. Query: '{query}'")
        print("   " + "-" * 76)
        
        try:
            response = kernel.run(query)
            
            # Truncate long responses
            if len(response) > 250:
                display = response[:250] + "..."
            else:
                display = response
                
            print(f"   ✅ Response:\n   {display}")
        except Exception as e:
            print(f"   ⚠️  Error: {e}")

print("\n" + "=" * 80)
print("PHASE 4: ADVANCED WORKFLOW")
print("=" * 80)

# Test a workflow combining all three tools
workflow_query = """
Check my Calendly schedule for next week.
For each meeting, create a record in my Airtable 'Meetings' base.
Then create corresponding Cal.com event types for recurring meetings.
"""

print(f"\n🎯 Advanced Workflow:")
print(f"   {workflow_query.strip()}")
print("\n⚠️  Requires all tools authenticated!")
print("-" * 80)

try:
    response = kernel.run(workflow_query)
    print(f"✅ Response:\n{response[:400]}...")
except Exception as e:
    print(f"⚠️  Error: {e}")

print("\n" + "=" * 80)
print("📋 SUMMARY")
print("=" * 80)

print("\n🔗 Authentication URLs:")
for tool in tools_to_test:
    url = auth_urls.get(tool['slug'])
    if url:
        status = "✅" if "already connected" in url.lower() else "🔗"
        print(f"   {status} {tool['emoji']} {tool['name']}")
        print(f"      {url[:70]}...")
    else:
        print(f"   ❌ {tool['emoji']} {tool['name']}: Failed")

print("\n💡 Use Cases:")
print("\n   📆 Cal.com:")
print("      • 'Create a 15-minute coffee chat event type'")
print("      • 'Show my booking statistics for this month'")
print("      • 'Update my availability for next week'")

print("\n   📅 Calendly:")
print("      • 'List all my scheduled meetings'")
print("      • 'Cancel my 3pm meeting tomorrow'")
print("      • 'Create a new event type for team standups'")

print("\n   🗄️ Airtable:")
print("      • 'Add a new task: Review Q1 budget'")
print("      • 'Show all high-priority items in my tasks base'")
print("      • 'Update the status of task #123 to completed'")

print("\n🔄 Combined Workflows:")
print("   • 'Sync my Calendly meetings to Airtable'")
print("   • 'Create Cal.com events from my Airtable project list'")
print("   • 'Send Airtable summary of all meetings this week'")

print("\n" + "=" * 80)
print("TEST COMPLETE!")
print("=" * 80)
print("\n🎉 You now have access to:")
print("   • 3 Calendar/Scheduling tools")
print("   • 1 Database/Collaboration tool")
print("   • Unlimited automation possibilities!")
print()
