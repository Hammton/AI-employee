#!/usr/bin/env python3
"""
Composio Auth URL Validation Script

This script validates OAuth URLs before presenting them to users.
Prevents the "expired link" and "invalid URL" problems.

Usage:
    python validate_auth_url.py <url>
    
Returns:
    Exit code 0 if URL is valid, 1 if invalid
    Prints JSON with validation result
"""

import sys
import json
import re
from urllib.parse import urlparse
import os

# Optional: Use requests for HTTP validation
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


def validate_url_format(url: str) -> dict:
    """Validate URL format without making HTTP request."""
    result = {
        "valid": False,
        "url": url,
        "checks": [],
        "errors": []
    }
    
    # Check 1: Not empty
    if not url:
        result["errors"].append("URL is empty")
        return result
    result["checks"].append("not_empty")
    
    # Check 2: Starts with https
    if not url.startswith("https://"):
        result["errors"].append("URL must use HTTPS")
        return result
    result["checks"].append("uses_https")
    
    # Check 3: Valid URL structure
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            result["errors"].append("Invalid URL structure")
            return result
        result["checks"].append("valid_structure")
    except Exception as e:
        result["errors"].append(f"URL parse error: {e}")
        return result
    
    # Check 4: Known OAuth providers (Composio uses these)
    known_domains = [
        "composio.dev",
        "app.composio.dev",
        "accounts.google.com",
        "github.com",
        "slack.com",
        "notion.so",
        "app.asana.com",
        "api.notion.com",
        "login.microsoftonline.com"
    ]
    
    domain = parsed.netloc.lower()
    is_known = any(known in domain for known in known_domains)
    
    if is_known:
        result["checks"].append("known_oauth_provider")
    else:
        # Not necessarily an error, just a warning
        result["checks"].append("unknown_provider")
    
    # Check 5: Has required OAuth parameters (for Composio redirects)
    if "composio" in domain:
        # Composio URLs should have certain patterns
        if "/auth/" in url or "/connect/" in url or "/app/" in url:
            result["checks"].append("valid_composio_path")
        else:
            result["errors"].append("Composio URL missing auth path")
            return result
    
    # All format checks passed
    result["valid"] = True
    return result


def validate_url_http(url: str, timeout: int = 5) -> dict:
    """Validate URL by making HTTP HEAD request."""
    result = {
        "accessible": False,
        "status_code": None,
        "redirect_url": None,
        "error": None
    }
    
    if not REQUESTS_AVAILABLE:
        result["error"] = "requests library not available"
        return result
    
    try:
        response = requests.head(
            url, 
            timeout=timeout, 
            allow_redirects=True,
            headers={"User-Agent": "PocketAgent/1.0"}
        )
        result["status_code"] = response.status_code
        result["accessible"] = response.status_code < 400
        
        # Check for redirects
        if response.history:
            result["redirect_url"] = response.url
            
    except requests.Timeout:
        result["error"] = "Request timed out"
    except requests.ConnectionError:
        result["error"] = "Connection failed"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def generate_fallback_url(app_slug: str, user_id: str = None) -> str:
    """Generate fallback Composio URL if primary fails."""
    base_url = f"https://app.composio.dev/app/{app_slug}"
    if user_id:
        base_url += f"?entity_id={user_id}"
    return base_url


def validate_and_fix(url: str, app_slug: str = None, user_id: str = None) -> dict:
    """
    Complete validation with automatic fallback.
    
    Returns:
        {
            "original_url": str,
            "final_url": str,  # The URL to present to user
            "valid": bool,
            "used_fallback": bool,
            "validation_result": dict
        }
    """
    # Step 1: Format validation
    format_result = validate_url_format(url)
    
    result = {
        "original_url": url,
        "final_url": url,
        "valid": format_result["valid"],
        "used_fallback": False,
        "validation_result": format_result
    }
    
    if not format_result["valid"]:
        # Format invalid - use fallback
        if app_slug:
            fallback = generate_fallback_url(app_slug, user_id)
            result["final_url"] = fallback
            result["used_fallback"] = True
            result["valid"] = True  # Fallback is valid
        return result
    
    # Step 2: Optional HTTP validation (skip in CI/test environments)
    if REQUESTS_AVAILABLE and os.environ.get("VALIDATE_HTTP", "false").lower() == "true":
        http_result = validate_url_http(url)
        result["http_validation"] = http_result
        
        if not http_result["accessible"]:
            # HTTP check failed - use fallback
            if app_slug:
                fallback = generate_fallback_url(app_slug, user_id)
                result["final_url"] = fallback
                result["used_fallback"] = True
    
    return result


# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({
            "error": "Usage: validate_auth_url.py <url> [app_slug] [user_id]"
        }))
        sys.exit(1)
    
    url = sys.argv[1]
    app_slug = sys.argv[2] if len(sys.argv) > 2 else None
    user_id = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = validate_and_fix(url, app_slug, user_id)
    print(json.dumps(result, indent=2))
    
    sys.exit(0 if result["valid"] else 1)
