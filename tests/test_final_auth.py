"""Test the fixed get_auth_url with auth_config_map"""
from composio import Composio
from composio_langchain import LangchainProvider
import os
from dotenv import load_dotenv

load_dotenv()

# Simulate what kernel.py does
composio_client = Composio(
    api_key=os.getenv("COMPOSIO_API_KEY"),
    provider=LangchainProvider()
)

# Load auth_config_map
auth_config_map = {}
try:
    configs = composio_client.auth_configs.list()
    if hasattr(configs, 'items'):
        for cfg in configs.items:
            if hasattr(cfg, 'name') and hasattr(cfg, 'id'):
                app_name = cfg.name.split('-')[0].strip().lower().replace(' ', '')
                auth_config_map[app_name] = cfg.id
                print(f"Mapped: {app_name} -> {cfg.id}")
    print(f"\nTotal mappings: {len(auth_config_map)}\n")
except Exception as e:
    print(f"Error loading configs: {e}")

# Test get_auth_url logic
slug = "googlecalendar"
auth_config_id = auth_config_map.get(slug)

print(f"Testing auth URL generation for '{slug}'")
print(f"Auth Config ID: {auth_config_id}")

if auth_config_id:
    try:
        result = composio_client.connected_accounts.link(
            user_id="default_user",
            auth_config_id=auth_config_id
        )
        print(f"\nResult type: {type(result)}")
        
        # Extract URL
        if hasattr(result, 'url'):
            print(f"✓ URL found: {result.url}")
        elif hasattr(result, 'link'):
            print(f"✓ Link found: {result.link}")
        elif hasattr(result, 'redirect_url'):
            print(f"✓ Redirect URL found: {result.redirect_url}")
        else:
            print(f"Result: {result}")
            attrs = [x for x in dir(result) if not x.startswith('_')]
            print(f"Attributes: {attrs}")
            
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print("✗ No auth config found!")
