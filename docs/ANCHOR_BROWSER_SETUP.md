# Anchor Browser Integration - Complete Setup

## Overview
Anchor Browser has been integrated into PocketAgent to provide web browsing capabilities. The agent can now visit URLs, search the web, take screenshots, and interact with web pages.

## What Was Done

### 1. Added Anchor Browser to Essential Tools
Updated `kernel.py` to include Anchor Browser essential tools:
- `ANCHOR_BROWSER_PERFORM_WEB_TASK` - Main tool for web browsing
- `ANCHOR_BROWSER_GET_PROFILE` - Get browser profile info
- `ANCHOR_BROWSER_LIST_PROFILES` - List available profiles

### 2. Added Slug Mappings
Added mappings in both `check_connection()` and `get_auth_url()` methods:
- `'anchorbrowser'` -> `'anchor_browser'`
- `'browser'` -> `'anchor_browser'`

This allows users to connect using natural names like "browser" or "anchor browser".

### 3. Dynamic System Prompt
The system prompt now dynamically adjusts based on whether Anchor Browser is connected:

**When Connected:**
```
WEB BROWSING: You HAVE web browsing capabilities through Anchor Browser! You can:
- Visit any URL and extract content
- Search the web for information
- Take screenshots of websites
- Interact with web pages
- Navigate and explore websites
```

**When Not Connected:**
```
WEB BROWSING: You do NOT have web browsing capabilities. 
If the user asks you to browse the web, politely explain that you don't have 
that capability and suggest they connect Anchor Browser.
```

### 4. Auto-Detection
When the kernel starts, it automatically detects all connected apps including Anchor Browser and loads their tools.

## How to Connect Anchor Browser

### Option 1: Using the Script
```bash
python connect_anchor_browser.py
```

This will:
1. Check if Anchor Browser is already connected
2. Generate an authentication URL if not connected
3. Display the URL for you to visit

### Option 2: Through the Agent
Users can ask the agent:
- "Connect anchor browser"
- "I need web browsing"
- "Connect browser"

The agent will use the `generate_auth_link` tool to provide the connection URL.

### Option 3: Direct Composio Dashboard
Visit https://app.composio.dev and connect Anchor Browser manually.

## Authentication URL
The generated URL looks like:
```
https://connect.composio.dev/link/lk_aIb1hW9ntXRN
```

Visit this URL to complete the OAuth flow and connect Anchor Browser to your account.

## Available Capabilities

Once connected, the agent can:

1. **Visit URLs**: Extract content from any webpage
2. **Search the Web**: Perform web searches and get results
3. **Take Screenshots**: Capture screenshots of websites
4. **Interact with Pages**: Click buttons, fill forms, navigate
5. **Extract Data**: Scrape structured data from websites

## Example Usage

### User Query:
"Visit https://fortune.com/2026/01/29/100-percent-of-code-at-anthropic-and-openai-is-now-ai-written-boris-cherry-roon/ and summarize the article"

### Agent Response (When Connected):
The agent will:
1. Use `ANCHOR_BROWSER_PERFORM_WEB_TASK` to visit the URL
2. Extract the article content
3. Provide a summary

### Agent Response (When Not Connected):
"I don't have web browsing capabilities yet. Would you like me to help you connect Anchor Browser? I can generate an authentication link for you."

## Testing

### Test Connection Status
```python
from kernel import AgentKernel

kernel = AgentKernel(user_id="+254708235245@c.us")
kernel.setup()

is_connected = kernel.check_connection("anchor_browser")
print(f"Anchor Browser connected: {is_connected}")
```

### Test Web Browsing
After connecting, send a message through WhatsApp:
```
Visit https://example.com and tell me what you see
```

## Troubleshooting

### Issue: "No connected account found for toolkit anchor_browser"
**Solution**: The user hasn't connected Anchor Browser yet. Generate an auth link using `connect_anchor_browser.py` or ask the agent to generate one.

### Issue: Tools not loading
**Solution**: 
1. Check if auto-detection is working: `kernel.active_apps` should include `'ANCHOR_BROWSER'`
2. Verify the connection: `kernel.check_connection('anchor_browser')` should return `True`
3. Restart the server to reload tools

### Issue: Agent claims to have browsing but fails
**Solution**: This was the original issue - the LLM was hallucinating. Now fixed with dynamic system prompt that only claims browsing capabilities when actually connected.

## Files Modified
- `kernel.py` - Added Anchor Browser support, slug mappings, dynamic system prompt
- `connect_anchor_browser.py` - Script to connect Anchor Browser

## Next Steps

1. **Connect Anchor Browser**: Run `python connect_anchor_browser.py` and visit the auth URL
2. **Restart Server**: Restart `main_v2.py` to reload with the new configuration
3. **Test**: Send a URL through WhatsApp and verify the agent can browse it

## Status
✅ **READY** - Anchor Browser integration is complete and ready to use once connected.

The agent will automatically detect when Anchor Browser is connected and enable web browsing capabilities.
