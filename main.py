from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import sys

load_dotenv()

# Check for required Anthropic API key
if not os.getenv("ANTHROPIC_API_KEY"):
    print("\n⚠️  Error: ANTHROPIC_API_KEY environment variable is not set.", file=sys.stderr)
    print("Please set your Anthropic API key in the .env file or as an environment variable.", file=sys.stderr)
    print("Press CTRL+C to stop the server.\n", file=sys.stderr)
    sys.exit(1)

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[dict[str, str]]

@app.post("/chat")
def chat(request: ChatRequest):
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1024,
        messages=request.messages
    )
    return {"response": response.content}

@app.get("/")
def read_root():
    return FileResponse('index.html')
