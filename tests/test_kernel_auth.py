"""Test the kernel auth URL generation."""
from dotenv import load_dotenv
load_dotenv()

from kernel import AgentKernel

k = AgentKernel()
print("Kernel created")
print(f"composio_client: {k.composio_client}")

# Test get_auth_url
try:
    url = k.get_auth_url('gmail')
    print(f"✅ Auth URL: {url}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
