"""Simple test of URL generation logic"""

def generate_auth_url(app_name: str) -> str:
    """Test version of get_auth_url"""
    slug = app_name.lower().replace(" ", "")
    auth_url = f"https://app.composio.dev/app/{slug}/connect?entity_id=default_user"
    return auth_url

# Test cases
test_apps = [
    ("Google Calendar", "https://app.composio.dev/app/googlecalendar/connect?entity_id=default_user"),
    ("Gmail", "https://app.composio.dev/app/gmail/connect?entity_id=default_user"),
    ("Slack", "https://app.composio.dev/app/slack/connect?entity_id=default_user"),
    ("github", "https://app.composio.dev/app/github/connect?entity_id=default_user"),
]

print("Testing Auth URL Generation")
print("=" * 80)

all_passed = True
for app_name, expected in test_apps:
    result = generate_auth_url(app_name)
    passed = result == expected
    all_passed = all_passed and passed
    
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"\n{status} | App: '{app_name}'")
    print(f"  Result:   {result}")
    if not passed:
        print(f"  Expected: {expected}")

print("\n" + "=" * 80)
print(f"\nOverall: {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
