"""
Improved error handling for Composio connection errors.
This module provides utilities to detect and handle "ConnectedAccountNotFound" errors
by automatically generating authentication links.
"""

import re
import logging

logger = logging.getLogger(__name__)


def extract_missing_toolkit(error_message: str) -> str | None:
    """
    Extract the toolkit name from a Composio connection error.
    
    Example error:
    "No connected account found for entity ID 86152916787450@lid for toolkit googlesheets"
    
    Returns:
        Toolkit name (e.g., "googlesheets") or None if not found
    """
    # Pattern: "for toolkit <name>"
    match = re.search(r'for toolkit (\w+)', error_message, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    
    # Alternative pattern: "toolkit: <name>"
    match = re.search(r'toolkit:\s*(\w+)', error_message, re.IGNORECASE)
    if match:
        return match.group(1).lower()
    
    return None


def is_connection_error(error_message: str) -> bool:
    """
    Check if an error is a Composio connection error.
    
    Returns:
        True if this is a "ConnectedAccountNotFound" error
    """
    error_lower = error_message.lower()
    
    # Check for common connection error patterns
    patterns = [
        'no connected account found',
        'connectedaccountnotfound',
        'actionexecute_connectedaccountnotfound',
        'not connected',
        'connection not found',
    ]
    
    return any(pattern in error_lower for pattern in patterns)


def handle_connection_error(kernel, error_message: str) -> str:
    """
    Handle a Composio connection error by generating an auth link.
    
    Args:
        kernel: AgentKernel instance
        error_message: The error message from Composio
        
    Returns:
        User-friendly message with auth link
    """
    # Extract the missing toolkit
    toolkit = extract_missing_toolkit(error_message)
    
    if not toolkit:
        return f"⚠️ Connection error: {error_message}\n\nPlease connect the required app using /connect <app_name>"
    
    # Generate auth link
    try:
        auth_url = kernel.get_auth_url(toolkit)
        
        if auth_url is None:
            # Already connected - this shouldn't happen, but handle it
            return f"⚠️ {toolkit.upper()} appears to be connected, but there was an error. Try reconnecting:\n\nUse /connect {toolkit}"
        
        # Format toolkit name nicely
        toolkit_display = toolkit.replace('google', 'Google ').replace('sheets', 'Sheets').replace('docs', 'Docs').replace('calendar', 'Calendar').strip()
        
        return f"""⚠️ {toolkit_display} is not connected yet.

To use {toolkit_display}, please connect your account:

🔗 {auth_url}

After connecting, I'll be able to help you with {toolkit_display}!"""
        
    except Exception as e:
        logger.error(f"Failed to generate auth link for {toolkit}: {e}")
        return f"⚠️ {toolkit.upper()} is not connected. Please use /connect {toolkit} to connect it."


def wrap_kernel_run(kernel, goal: str) -> str:
    """
    Wrapper around kernel.run() that handles connection errors gracefully.
    
    Args:
        kernel: AgentKernel instance
        goal: User's goal/query
        
    Returns:
        Response from kernel or user-friendly error message
    """
    try:
        result = kernel.run(goal)
        
        # Check if the result itself contains a connection error
        # (This happens when the error is returned as a string)
        if isinstance(result, str) and is_connection_error(result):
            return handle_connection_error(kernel, result)
        
        return result
        
    except Exception as e:
        error_message = str(e)
        
        # Check if this is a connection error
        if is_connection_error(error_message):
            return handle_connection_error(kernel, error_message)
        
        # For other errors, return the original error
        logger.error(f"Kernel error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"⚠️ An error occurred: {error_message[:200]}"


# Example usage in main_v2.py:
"""
# OLD CODE:
result = user_kernel.run(msg_text)

# NEW CODE:
from improved_error_handling import wrap_kernel_run
result = wrap_kernel_run(user_kernel, msg_text)
"""
