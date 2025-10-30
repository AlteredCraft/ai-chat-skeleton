from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import sys
import logging

load_dotenv()

# Configure logging
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Configure warnings and errors to go to stderr
class StderrFilter(logging.Filter):
    def filter(self, record):
        return record.levelno >= logging.WARNING

stderr_handler = logging.StreamHandler(sys.stderr)
stderr_handler.setLevel(logging.WARNING)
stderr_handler.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
stderr_handler.addFilter(StderrFilter())

# Update root logger to route warnings/errors to stderr
logging.root.handlers[0].addFilter(lambda record: record.levelno < logging.WARNING)
logging.root.addHandler(stderr_handler)

logger = logging.getLogger("app")

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
    logger.info(f"Received chat request | num_messages={len(request.messages)}")
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
