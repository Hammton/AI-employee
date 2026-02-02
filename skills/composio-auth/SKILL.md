---
name: composio-auth
description: Robust Composio OAuth authentication and connection management. Use when user needs to connect apps (Gmail, Sheets, Asana, etc.), when auth links fail or expire, when checking connection status, or when troubleshooting "not authenticated" errors. Handles link generation, validation, and retry logic.
---

# Composio Auth Skill

## Purpose
Provides **bulletproof OAuth authentication** for Composio tool integrations. Solves the problem of expired links, failed connections, and flaky auth URLs.

## When This Skill Activates
- User asks to "connect" or "authorize" an app
- Tool execution fails with "not authenticated" or "no connection" errors
- User asks "am I connected to X?"
- Auth link generation fails or returns invalid URL

## Core Philosophy: Validate Before Presenting

Never present a URL to the user unless you've verified it will work.

### The 3-Step Auth Pattern

```
1. CHECK → Is user already connected?
2. GENERATE → Create fresh auth URL (not cached)
3. VALIDATE → Verify URL is accessible before presenting
```

## Workflow

### Step 1: Normalize App Name
Map common variations to actual Composio slugs:

| User Says | Composio Slug |
|-----------|---------------|
| gmail, google mail, googlemail | gmail |
| sheets, google sheets, spreadsheet | googlesheets |
| docs, google docs | googledocs |
| calendar, google calendar | googlecalendar |
| drive, google drive | googledrive |
| asana, tasks | asana |
| notion | notion |
| slack | slack |
| github | github |
| anchor browser, browser | anchor_browser |

### Step 2: Check Existing Connection
Before generating a new URL, verify the user isn't already connected:

```python
# Use connected_accounts.list() - NOT session.toolkits()
accounts = client.connected_accounts.list(user_ids=[user_id])
for account in accounts.items:
    if account.toolkit.slug == app_slug and account.status == "ACTIVE":
        return "Already connected!"
```

### Step 3: Generate Fresh Auth URL
Use the official pattern - **always generate fresh**, never cache:

```python
connection_request = session.authorize(app_slug)
auth_url = connection_request.redirect_url
```

### Step 4: Validate URL (NEW - Critical Fix)
Before presenting to user, validate the URL:

```python
# Quick check - does the URL look valid?
if not auth_url or not auth_url.startswith("https://"):
    # Regenerate or use fallback
    
# Optional: HTTP HEAD request to verify accessibility
import requests
try:
    response = requests.head(auth_url, timeout=5, allow_redirects=True)
    if response.status_code >= 400:
        # URL is broken, regenerate
except:
    # URL not accessible, use fallback
```

## Fallback URLs

If `session.authorize()` fails, use direct Composio app URLs:

```
https://app.composio.dev/app/{slug}
```

With explicit entity_id parameter:
```
https://app.composio.dev/app/{slug}?entity_id={user_id}
```

## Common Failure Modes

### 1. Expired OAuth State
**Symptom**: User clicks link, gets "invalid state" error
**Solution**: Generate fresh URL, don't reuse old ones

### 2. Session Not Initialized
**Symptom**: `composio_session is None`
**Solution**: Call `setup()` first to initialize session

### 3. Wrong App Slug
**Symptom**: "Toolkit not found" error
**Solution**: Use slug_mappings to normalize names

### 4. Rate Limited
**Symptom**: 429 errors from Composio API
**Solution**: Implement exponential backoff, use cached connections

## Response Patterns

### When Already Connected
```
✅ You're already connected to Google Sheets! 
You can start using it right away - try "create a new spreadsheet"
```

### When Auth Needed (Give Clear Instructions)
```
📱 To connect Google Sheets:

1. Click this link: [AUTH_URL]
2. Log in with your Google account
3. Grant the requested permissions
4. Come back and say "done" or try your request again

⏱️ This link expires in 10 minutes.
```

### When Auth Fails
```
❌ I couldn't generate an auth link for Google Sheets.

Try manually:
1. Go to https://app.composio.dev
2. Click "Add Connection"
3. Search for "Google Sheets"
4. Complete the OAuth flow

Then come back and I'll detect your new connection!
```

## Script Reference

For deterministic auth handling, use: `scripts/validate_auth_url.py`

## Troubleshooting Guide

See: `references/composio_auth_troubleshooting.md`
