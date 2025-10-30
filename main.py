from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import sys
from logger import logger

load_dotenv()

# Log startup information
logger.info("Starting application")
logger.debug("Environment variables loaded")

# Check for required Anthropic API key
if not os.getenv("ANTHROPIC_API_KEY"):
    logger.error("ANTHROPIC_API_KEY environment variable is not set")
    logger.error("Please set your Anthropic API key in the .env file or as an environment variable")
    sys.exit(1)

app = FastAPI()

class ChatRequest(BaseModel):
    messages: list[dict[str, str]]

@app.post("/chat")
def chat(request: ChatRequest):
    logger.info("Received chat request", num_messages=len(request.messages))
    logger.debug(f"Chat messages: {request.messages}")

    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        logger.debug("Sending request to Anthropic API")

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            messages=request.messages
        )

        logger.info("Successfully received response from Anthropic API")
        logger.debug(f"Response: {response.content}")
        return {"response": response.content}
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise

@app.get("/")
def read_root():
    logger.debug("Serving index.html")
    return FileResponse('index.html')
