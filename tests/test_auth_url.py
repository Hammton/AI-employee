"""Test the updated get_auth_url method"""
import sys
sys.path.insert(0, '.')

from kernel import AgentKernel

# Initialize kernel
kernel = AgentKernel()
kernel.setup()

# Test various app names
test_apps = [
    "Google Calendar",
    "Gmail",
    "googlecalendar",
    "Slack"
]

print("Testing get_auth_url method:\n")
print("=" * 70)

for app in test_apps:
    url = kernel.get_auth_url(app)
    print(f"\nApp: '{app}'")
    print(f"URL: {url}")
    
    # Verify URL format
    expected_slug = app.lower().replace(" ", "")
    expected_url = f"https://app.composio.dev/app/{expected_slug}/connect?entity_id=default_user"
    
    if url == expected_url:
        print("✓ PASS")
    else:
        print(f"✗ FAIL - Expected: {expected_url}")

print("\n" + "=" * 70)
print("\nTest complete!")
