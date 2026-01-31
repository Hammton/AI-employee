from dotenv import load_dotenv
load_dotenv()
import os
from langchain_openai import ChatOpenAI

api_key = os.environ.get("OPENROUTER_API_KEY")
model = os.environ.get("LLM_MODEL", "google/gemini-3-flash-preview")

print(f"Testing Model: {model}")

llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    model=model
)

try:
    response = llm.invoke("Hello, who are you?")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"Error: {e}")
