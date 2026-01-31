# How to Connect Gmail to Composio

Since the agent-based connection is complex, here's the simpler way:

## Option 1: Use Composio Dashboard (Recommended)

1. Go to https://platform.composio.dev
2. Log in with your API key: `ak_-4Auk5vJV_6ULAxOGXla`
3. Navigate to "Connected Accounts" or "Integrations"
4. Find Gmail and click "Connect"
5. Authorize with your Google account
6. Done! Your agent can now access Gmail

## Option 2: Use Composio CLI

```bash
# Login
composio login

# Connect Gmail
composio add gmail

# This will open a browser for OAuth
```

## Option 3: Generate Connection URL Programmatically

```python
from composio import Composio

composio = Composio(api_key="ak_-4Auk5vJV_6ULAxOGXla")

# Get connection URL
connection_request = composio.connected_accounts.initiate(
    integration_id="gmail",
    entity_id="test_user"  # Your user ID
)

print(f"Connect Gmail here: {connection_request.redirectUrl}")
```

## After Connecting

Once Gmail is connected, your agent will automatically have access to Gmail tools like:
- GMAIL_FETCH_EMAILS
- GMAIL_SEND_EMAIL  
- GMAIL_SEARCH_EMAILS
- etc.

Then you can ask: "Check my latest emails" and it will work!
