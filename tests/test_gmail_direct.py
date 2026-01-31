"""Test Gmail directly using Composio execute"""

import os
from typing import Any, cast
from dotenv import load_dotenv

load_dotenv()

from composio import Composio

ENTITY_ID = "pg-test-f0f04ef6-96e2-46a2-ba81-6542eb56f345"
TEST_RECIPIENT = "hammtonndeke@gmail.com"
TEST_SUBJECT = "Quick hello from Composio"
TEST_BODY = (
    "Hi Hammton,\n\n"
    "Just a quick test email sent via Composio to confirm Gmail integration. "
    "If you see this, the pipeline is working as expected.\n\n"
    "Best,\n"
    "Composio Test"
)

composio = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("=" * 60)
print("TESTING GMAIL DIRECT EXECUTION")
print("=" * 60)

# Get entity
entity = composio.get_entity(id=ENTITY_ID)

# Check Gmail connection
connection = entity.get_connection(app="gmail")
print(f"\n✅ Gmail connection: {connection.status}")
print(f"   Connection ID: {connection.id}\n")

# Execute Gmail action directly
print("Fetching latest emails...\n")

try:
    from composio.client.enums import Action

    execute_action = getattr(entity, "execute_action", None)
    if callable(execute_action):
        result = cast(
            dict[str, Any],
            execute_action(
                action=Action.GMAIL_FETCH_EMAILS,
                params={
                    "max_results": 3,
                    "label_ids": ["INBOX"],
                    "include_payload": False,
                },
            ),
        )
    else:
        result = cast(
            dict[str, Any],
            entity.execute(
                action=Action.GMAIL_FETCH_EMAILS,
                params={
                    "max_results": 3,
                    "label_ids": ["INBOX"],
                    "include_payload": False,
                },
            ),
        )

    print("=" * 60)
    print("EMAILS:")
    print("=" * 60)

    if result.get("successful"):
        data = result.get("data", {})
        emails = data.get("messages", [])

        for i, email in enumerate(emails, 1):
            print(f"\n{i}. From: {email.get('sender', 'Unknown')}")
            print(f"   Subject: {email.get('subject', 'No subject')}")
            print(f"   Date: {email.get('messageTimestamp', 'Unknown')}")

        print("\n" + "=" * 60)
        if not emails:
            hint = data.get("composio_execution_message")
            if hint:
                print(f"ℹ️ Hint: {hint}")
        print(f"✅ Successfully fetched {len(emails)} emails!")
    else:
        print(f"❌ Error: {result.get('error')}")

    print("\n" + "=" * 60)
    print("CREATING EMAIL DRAFT:")
    print("=" * 60)

    create_result = cast(
        dict[str, Any],
        entity.execute(
            action=Action.GMAIL_CREATE_EMAIL_DRAFT,
            params={
                "recipient_email": TEST_RECIPIENT,
                "subject": TEST_SUBJECT,
                "body": TEST_BODY,
                "is_html": False,
            },
        ),
    )

    if create_result.get("successful"):
        draft_id = create_result.get("data", {}).get("id")
        print(f"✅ Draft created for {TEST_RECIPIENT}")
        print(f"   Draft ID: {draft_id}")
        print("   Open Gmail to review and send the draft.")
    else:
        print(f"❌ Draft error: {create_result.get('error')}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
