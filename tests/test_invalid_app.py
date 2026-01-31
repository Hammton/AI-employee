from dotenv import load_dotenv
load_dotenv()
from kernel import AgentKernel

k = AgentKernel()
print("Testing invalid app name...")
try:
    url = k.get_auth_url("to gmail")
    print(f"URL: {url}")
except Exception as e:
    print(f"Error: {e}")
