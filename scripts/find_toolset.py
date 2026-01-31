try:
    from composio import ComposioToolSet

    print("ComposioToolSet found in composio")
except ImportError:
    print("ComposioToolSet NOT found in composio")

try:
    from composio.adapters.openai import ComposioToolSet

    print("ComposioToolSet found in composio.adapters.openai")
except ImportError:
    print("ComposioToolSet NOT found in composio.adapters.openai")
