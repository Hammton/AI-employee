# Composio Auth Troubleshooting Guide

## Quick Reference

### Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "Not authenticated" | User hasn't connected app | Generate new auth link |
| "Invalid state parameter" | OAuth state expired | Generate fresh URL, don't reuse |
| "Toolkit not found" | Wrong app slug | Use slug mapping table |
| "connection_request is None" | Session not initialized | Call setup() first |
| "Rate limited (429)" | Too many API calls | Wait 60s, implement backoff |
| "Entity not found" | Wrong user_id format | Check user_id matches exactly |

### App Slug Mappings

```python
SLUG_MAPPINGS = {
    # Google Apps
    'googlemail': 'gmail',
    'google_mail': 'gmail',
    'googlemaps': 'googlemaps',
    'googlecalendar': 'googlecalendar',
    'google_calendar': 'googlecalendar',
    'googlesheets': 'googlesheets',
    'google_sheets': 'googlesheets',
    'googledrive': 'googledrive',
    'google_drive': 'googledrive',
    'googlecontacts': 'googlecontacts',
    'googledocs': 'googledocs',
    'google_docs': 'googledocs',
    'googleslides': 'googleslides',
    
    # Other apps
    'anchorbrowser': 'anchor_browser',
    'browser': 'anchor_browser',
    'linkedin': 'linkedin',
}
```

### OAuth URL Patterns

**Composio Direct Auth:**
```
https://app.composio.dev/auth/connect/{toolkit_slug}?entityId={user_id}
```

**Composio App Page:**
```
https://app.composio.dev/app/{toolkit_slug}?entity_id={user_id}
```

**Google OAuth:**
```
https://accounts.google.com/o/oauth2/v2/auth?...
```

### Validation Checklist

1. ✅ URL starts with `https://`
2. ✅ Contains valid domain (composio.dev, google.com, etc.)
3. ✅ Has required OAuth parameters
4. ✅ Not a cached/expired URL
5. ✅ Entity ID matches user

### Connection Check Pattern

```python
def is_connected(client, user_id: str, app_slug: str) -> bool:
    """Check if user has active connection to app."""
    try:
        accounts = client.connected_accounts.list(user_ids=[user_id])
        for account in accounts.items:
            if (account.status == "ACTIVE" and 
                hasattr(account, 'toolkit') and 
                account.toolkit and
                getattr(account.toolkit, 'slug', '').lower() == app_slug.lower()):
                return True
    except Exception:
        pass
    return False
```

### Fresh URL Generation

```python
def get_fresh_auth_url(session, app_slug: str) -> str:
    """Generate a fresh OAuth URL - never cache these."""
    try:
        connection_request = session.authorize(app_slug)
        
        # Try different attribute names (API versions differ)
        for attr in ['redirect_url', 'redirectUrl', 'url', 'auth_url']:
            if hasattr(connection_request, attr):
                url = getattr(connection_request, attr)
                if url:
                    return url
        
        # Last resort: string conversion
        return str(connection_request)
        
    except Exception as e:
        # Log error, return fallback
        return f"https://app.composio.dev/app/{app_slug}"
```

### Retry Logic

```python
import time

def authorize_with_retry(session, app_slug: str, max_attempts: int = 3) -> str:
    """Authorize with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            url = get_fresh_auth_url(session, app_slug)
            if url and url.startswith("https://"):
                return url
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2 ** attempt)  # 1s, 2s, 4s
            else:
                raise
    return None
```

## Deep Dive: Why Auth Links Fail

### Problem 1: OAuth State Timeout

OAuth uses a "state" parameter to prevent CSRF attacks. This state:
- Is generated when you create the auth URL
- Expires after ~10 minutes
- Must match when user returns from OAuth provider

**Solution:** Always generate fresh URLs, never cache them.

### Problem 2: Entity ID Mismatch

Composio scopes connections to "entities" (users). If:
- You generate URL with entity_id="user_123"
- But your session uses user_id="user123" 

The connection won't be found.

**Solution:** Use consistent user IDs everywhere.

### Problem 3: Session Staleness

The Composio session can become stale if:
- Long time since initialization
- API token expired
- Network issues

**Solution:** Re-initialize session before auth operations:
```python
if not self.composio_session:
    self.setup()
```

### Problem 4: Rate Limiting

Composio has rate limits. Symptoms:
- 429 HTTP errors
- Slow/failed responses
- Intermittent failures

**Solution:** 
- Cache connection checks (not URLs!)
- Implement backoff
- Check connections once per session, not per request

## Testing Auth Flow

### Manual Test

1. Start fresh session
2. Request auth for unconnected app
3. Verify URL is valid (click it)
4. Complete OAuth flow
5. Verify connection detected
6. Try tool execution

### Automated Test

```python
def test_auth_flow():
    kernel = AgentKernel(user_id="test_user")
    kernel.setup()
    
    # Should not be connected initially
    assert not kernel.check_connection("github")
    
    # Should generate valid URL
    url = kernel.get_auth_url("github")
    assert url.startswith("https://")
    
    # URL should be accessible
    import requests
    response = requests.head(url, allow_redirects=True)
    assert response.status_code < 400
```
