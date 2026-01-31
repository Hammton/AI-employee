import composio
import composio_openai
import inspect


def find_app(module):
    for name, obj in inspect.getmembers(module):
        if name == "App":
            print(f"Found App in {module.__name__}")
            return
        if inspect.ismodule(obj) and obj.__name__.startswith("composio"):
            try:
                find_app(obj)
            except RecursionError:
                pass


try:
    from composio import App

    print("from composio import App works")
except ImportError:
    pass

try:
    from composio.client.enums import App

    print("from composio.client.enums import App works")
except ImportError:
    pass

try:
    from composio_core import App

    print("from composio_core import App works")
except ImportError:
    pass
