#!/usr/bin/env python3
"""
Quick script to generate Google Sheets connection link for a user.
Run this to get the auth URL for connecting Google Sheets.
"""

import os
from dotenv import load_dotenv
from composio import Composio

# Load environment variables
load_dotenv()

def generate_sheets_auth_link(user_id: str):
    """Generate authentication link for Google Sheets."""
    
    composio_api_key = os.environ.get("COMPOSIO_API_KEY")
    if not composio_api_key:
        print("❌ COMPOSIO_API_KEY not found in .env file")
        return
    
    try:
        # Initialize Composio client
        composio_client = Composio(api_key=composio_api_key)
        
        # Create session for user
        session = composio_client.create(user_id=user_id)
        
        # Generate auth URL for Google Sheets
        connection_request = session.authorize("googlesheets")
        
        auth_url = connection_request.redirect_url
        
        print(f"\n✅ Google Sheets Authentication Link Generated!")
        print(f"\n📋 User ID: {user_id}")
        print(f"\n🔗 Auth URL:\n{auth_url}")
        print(f"\n📝 Instructions:")
        print(f"1. Send this link to the user via WhatsApp")
        print(f"2. User clicks the link and authorizes Google Sheets")
        print(f"3. After authorization, the agent will automatically have access to Google Sheets tools")
        print(f"\n")
        
        return auth_url
        
    except Exception as e:
        print(f"❌ Error generating auth link: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Get user ID from command line or use default
    import sys
    
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
    else:
        # Default user ID from the error message
        user_id = "86152916787450@lid"
    
    print(f"🔧 Generating Google Sheets auth link for user: {user_id}")
    generate_sheets_auth_link(user_id)
