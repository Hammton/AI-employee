#!/usr/bin/env python3
"""
QUICK FIX: Generate Google Sheets auth link and send it to the user via WhatsApp.

This script:
1. Generates the Google Sheets authentication link
2. Sends it to the user via WhatsApp
3. Waits for the user to connect
4. Confirms the connection

Run this now to fix the immediate issue!
"""

import os
import sys
import time
import requests
from dotenv import load_dotenv
from composio import Composio

# Load environment variables
load_dotenv()

# Configuration
USER_ID = "86152916787450@lid"  # From the error message
USER_PHONE = os.environ.get("USER_PHONE", "254708235245@c.us")
WPP_BRIDGE_URL = os.environ.get("WPP_BRIDGE_URL", "http://localhost:3000")


def send_whatsapp_message(phone: str, message: str) -> bool:
    """Send a message via WhatsApp."""
    try:
        response = requests.post(
            f"{WPP_BRIDGE_URL}/send-text",
            json={"to": phone, "text": message},
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Failed to send WhatsApp message: {e}")
        return False


def generate_auth_link(user_id: str, toolkit: str = "googlesheets"):
    """Generate authentication link for a toolkit."""
    composio_api_key = os.environ.get("COMPOSIO_API_KEY")
    if not composio_api_key:
        print("❌ COMPOSIO_API_KEY not found in .env file")
        return None
    
    try:
        # Initialize Composio client
        composio_client = Composio(api_key=composio_api_key)
        
        # Create session for user
        session = composio_client.create(user_id=user_id)
        
        # Generate auth URL
        connection_request = session.authorize(toolkit)
        auth_url = connection_request.redirect_url
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Error generating auth link: {e}")
        import traceback
        traceback.print_exc()
        return None


def check_connection(user_id: str, toolkit: str = "googlesheets"):
    """Check if user is connected to a toolkit."""
    composio_api_key = os.environ.get("COMPOSIO_API_KEY")
    if not composio_api_key:
        return False
    
    try:
        composio_client = Composio(api_key=composio_api_key)
        connected_accounts = composio_client.connected_accounts.list(user_ids=[user_id])
        
        for account in connected_accounts.items:
            if account.status == "ACTIVE" and hasattr(account, 'toolkit'):
                if account.toolkit and account.toolkit.slug.lower() == toolkit.lower():
                    return True
        
        return False
        
    except Exception as e:
        print(f"❌ Error checking connection: {e}")
        return False


def main():
    print("=" * 60)
    print("🔧 GOOGLE SHEETS CONNECTION FIX")
    print("=" * 60)
    print()
    
    # Step 1: Check if already connected
    print(f"📋 User ID: {USER_ID}")
    print(f"📱 Phone: {USER_PHONE}")
    print()
    print("Step 1: Checking current connection status...")
    
    if check_connection(USER_ID, "googlesheets"):
        print("✅ Google Sheets is already connected!")
        print()
        print("The error might be temporary. Try the original request again.")
        return
    
    print("❌ Google Sheets is NOT connected")
    print()
    
    # Step 2: Generate auth link
    print("Step 2: Generating authentication link...")
    auth_url = generate_auth_link(USER_ID, "googlesheets")
    
    if not auth_url:
        print("❌ Failed to generate auth link")
        return
    
    print(f"✅ Auth link generated!")
    print()
    print(f"🔗 {auth_url}")
    print()
    
    # Step 3: Send to user via WhatsApp
    print("Step 3: Sending link to user via WhatsApp...")
    
    message = f"""🔗 Google Sheets Connection Required

To create Google Sheets, please connect your Google account:

{auth_url}

Click the link above, authorize Google Sheets, and then try your request again!"""
    
    if send_whatsapp_message(USER_PHONE, message):
        print("✅ Message sent to user!")
    else:
        print("⚠️ Failed to send via WhatsApp. Please send this link manually:")
        print()
        print(auth_url)
    
    print()
    print("=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. User clicks the link and authorizes Google Sheets")
    print("2. User returns to WhatsApp")
    print("3. User retries their original request")
    print("4. Agent will now have access to Google Sheets tools!")
    print()
    print("To verify connection, run:")
    print(f"  python -c \"from fix_google_sheets_now import check_connection; print(check_connection('{USER_ID}'))\"")
    print()


if __name__ == "__main__":
    main()
