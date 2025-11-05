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

# Helper functions to parse environment variables
def get_env_int(key: str, default: int | None = None) -> int | None:
    """Get an integer from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning(f"Invalid integer value for {key}: {value}, using default: {default}")
        return default

def get_env_float(key: str, default: float | None = None) -> float | None:
    """Get a float from environment variable."""
    value = os.getenv(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        logger.warning(f"Invalid float value for {key}: {value}, using default: {default}")
        return default

def get_env_list(key: str, separator: str = ",") -> list[str] | None:
    """Get a list from environment variable (comma-separated)."""
    value = os.getenv(key)
    if value is None or value.strip() == "":
        return None
    return [item.strip() for item in value.split(separator) if item.strip()]

# Load Anthropic API parameters from environment variables
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
ANTHROPIC_MAX_TOKENS = get_env_int("ANTHROPIC_MAX_TOKENS", 1024)
ANTHROPIC_TEMPERATURE = get_env_float("ANTHROPIC_TEMPERATURE", 1.0)
ANTHROPIC_TOP_P = get_env_float("ANTHROPIC_TOP_P")
ANTHROPIC_TOP_K = get_env_int("ANTHROPIC_TOP_K")
ANTHROPIC_SYSTEM_PROMPT = os.getenv("ANTHROPIC_SYSTEM_PROMPT")
ANTHROPIC_STOP_SEQUENCES = get_env_list("ANTHROPIC_STOP_SEQUENCES")

# Log configured parameters
logger.info(f"Anthropic API configured | model={ANTHROPIC_MODEL} max_tokens={ANTHROPIC_MAX_TOKENS} temperature={ANTHROPIC_TEMPERATURE}")
if ANTHROPIC_TOP_P:
    logger.info(f"Using top_p={ANTHROPIC_TOP_P}")
if ANTHROPIC_TOP_K:
    logger.info(f"Using top_k={ANTHROPIC_TOP_K}")
if ANTHROPIC_SYSTEM_PROMPT:
    logger.info(f"System prompt configured | length={len(ANTHROPIC_SYSTEM_PROMPT)}")
if ANTHROPIC_STOP_SEQUENCES:
    logger.info(f"Stop sequences configured | count={len(ANTHROPIC_STOP_SEQUENCES)}")

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

        # Build parameters dictionary
        params = {
            "model": ANTHROPIC_MODEL,
            "max_tokens": ANTHROPIC_MAX_TOKENS,
            "messages": request.messages,
        }

        # Add optional parameters if configured
        if ANTHROPIC_TEMPERATURE is not None:
            params["temperature"] = ANTHROPIC_TEMPERATURE
        if ANTHROPIC_TOP_P is not None:
            params["top_p"] = ANTHROPIC_TOP_P
        if ANTHROPIC_TOP_K is not None:
            params["top_k"] = ANTHROPIC_TOP_K
        if ANTHROPIC_SYSTEM_PROMPT:
            params["system"] = ANTHROPIC_SYSTEM_PROMPT
        if ANTHROPIC_STOP_SEQUENCES:
            params["stop_sequences"] = ANTHROPIC_STOP_SEQUENCES

        response = client.messages.create(**params)

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
