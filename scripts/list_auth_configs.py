"""Try to list or create auth configs"""
from composio import Composio
import os
from dotenv import load_dotenv

load_dotenv()

client = Composio(api_key=os.getenv("COMPOSIO_API_KEY"))

print("Method 1: List existing auth configs\n")
try:
    if hasattr(client.auth_configs, 'list'):
        configs = client.auth_configs.list()
        print(f"✓ Got configs: {type(configs)}")
        
        if hasattr(configs, 'items'):
            print(f"  Found {len(configs.items)} configs")
            for cfg in configs.items[:5]:  # Show first 5
                print(f"\n  Config:")
                # Print all non-private attributes
                for attr in [x for x in dir(cfg) if not x.startswith('_')]:
                    try:
                        val = getattr(cfg, attr)
                        if not callable(val):
                            print(f"    {attr}: {val}")
                    except:
                        pass
        else:
            print(f"  Configs: {configs}")
    else:
        print(" ✗ No list method on auth_configs")
except Exception as e:
    print(f"✗ Failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("\nMethod 2: Try creating an auth config for googlecalendar\n")
try:
    # Check create signature
    import inspect
    sig = inspect.signature(client.auth_configs.create)
    print(f"create signature: {sig}")
except Exception as e:
    print(f"Could not get signature: {e}")
