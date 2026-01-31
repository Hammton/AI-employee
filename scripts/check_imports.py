try:
    import composio_openai
    import langchain_openai
    import playwright
    import fastapi

    print("Imports successful")
except ImportError as e:
    print(f"Import failed: {e}")
