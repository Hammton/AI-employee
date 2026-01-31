"""Test Composio client initialization directly"""
from composio import Composio
from composio_langchain import LangchainProvider
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("COMPOSIO_API_KEY")
print(f"API Key: {api_key[:10]}..." if api_key else "No API key found")

try:
    print("\nAttempt 1: Composio with api_key + provider")
    client = Composio(
        api_key=api_key,
        provider=LangchainProvider()
    )
    print("✓ Success!")
except Exception as e:
    print(f"✗ Failed: {e}")
    
    try:
        print("\nAttempt 2: Composio with just api_key")
        client = Composio(api_key=api_key)
        print("✓ Success!")
    except Exception as e2:
        print(f"✗ Failed: {e2}")
