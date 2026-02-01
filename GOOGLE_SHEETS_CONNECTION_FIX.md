# Google Sheets Connection Fix

## Problem
User tried to create a Google Sheet but got this error:
```
No connected account found for entity ID 86152916787450@lid for toolkit googlesheets
```

This means the user hasn't connected their Google Sheets account to Composio yet.

## Solution

### Option 1: Use the Agent's Built-in Tool (Recommended)

The agent already has a `generate_auth_link` tool that can create connection links. Just tell the agent:

**User message:**
```
I need to connect Google Sheets. Can you generate the auth link for me?
```

The agent will:
1. Check if Google Sheets is already connected
2. If not, generate an auth URL
3. Send the URL to the user
4. User clicks the link and authorizes
5. Agent automatically loads Google Sheets tools

### Option 2: Manual Script

Run the provided script:

```bash
python connect_google_sheets.py 86152916787450@lid
```

This will output an authentication URL that you can send to the user.

### Option 3: Direct API Call

If you want to do it programmatically in your code:

```python
from composio import Composio

composio_client = Composio(api_key="your_api_key")
session = composio_client.create(user_id="86152916787450@lid")
connection_request = session.authorize("googlesheets")
auth_url = connection_request.redirect_url

# Send auth_url to user via WhatsApp
```

## What Happens After Connection?

Once the user authorizes Google Sheets:

1. ✅ The connection is stored in Composio
2. ✅ The agent automatically detects the new connection
3. ✅ Google Sheets tools are loaded (CREATE_GOOGLE_SHEET1, BATCH_UPDATE, etc.)
4. ✅ User can now create and edit Google Sheets

## Available Google Sheets Tools

After connection, the agent will have access to:

- `GOOGLESHEETS_CREATE_GOOGLE_SHEET1` - Create new spreadsheets
- `GOOGLESHEETS_CREATE_SPREADSHEET_ROW` - Add rows
- `GOOGLESHEETS_CREATE_SPREADSHEET_COLUMN` - Add columns
- `GOOGLESHEETS_BATCH_UPDATE` - Update multiple cells
- `GOOGLESHEETS_GET_SPREADSHEET` - Read spreadsheet data
- `GOOGLESHEETS_CLEAR_VALUES` - Clear cell values
- And many more...

## Testing the Connection

After the user connects, test it:

```python
# Check if connected
kernel.check_connection("googlesheets")  # Should return True

# Try creating a sheet
kernel.run("Create a new Google Sheet called 'Test Sheet'")
```

## Common Issues

### Issue: "Already connected but still getting error"

**Solution:** Reload the agent's tools:
```python
kernel.add_apps(["GOOGLESHEETS"])
```

### Issue: "Auth link expired"

**Solution:** Generate a new auth link. Composio auth links expire after a certain time.

### Issue: "Wrong Google account"

**Solution:** 
1. User needs to disconnect the wrong account first
2. Generate a new auth link
3. User authorizes with the correct Google account

## Prevention

To avoid this issue in the future:

1. **Check connections before using tools:**
   ```python
   if not kernel.check_connection("googlesheets"):
       auth_url = kernel.get_auth_url("googlesheets")
       # Send auth_url to user
   ```

2. **Auto-detect connected apps:**
   The kernel already does this in `setup()` - it automatically loads tools for all connected apps.

3. **Graceful error handling:**
   When a tool fails with "ConnectedAccountNotFound", the agent should:
   - Detect the missing connection
   - Generate an auth link
   - Ask the user to connect
   - Retry after connection

## Related Files

- `kernel.py` - Contains `get_auth_url()` and `check_connection()` methods
- `connect_google_sheets.py` - Quick script to generate auth links
- `main_v2.py` - Main WhatsApp bot that handles user messages

## Next Steps

1. ✅ Generate auth link for user
2. ✅ Send link via WhatsApp
3. ✅ User authorizes Google Sheets
4. ✅ Agent automatically loads Google Sheets tools
5. ✅ Retry the original request (create Google Sheet)

The same process applies to ANY Composio integration (Gmail, Google Docs, Asana, etc.).
