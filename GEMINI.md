# Project Overview

This is a simple web-based chat application that uses the Anthropic API to power a conversation with an LLM. The application is built with Python and the FastAPI framework. The frontend is a simple HTML page with JavaScript to handle user input and display the chat responses.

## Building and Running

To run this project, you need to have `uv` installed. 

1. **Install dependencies:**

   ```bash
   uv add fastapi uvicorn anthropic
   ```

2. **Run the application:**

   ```bash
   uv run uvicorn main:app --reload
   ```

3. **Set the Anthropic API Key:**

   ```bash
   cp dist.env .env
   ```

   In `.env` replace `"YOUR_ANTHROPIC_API_KEY"` in `main.py` with your actual Anthropic API key.

## Development Conventions

- The backend is built with FastAPI.
- The frontend is a single HTML file with vanilla JavaScript.
- Dependencies are managed with `uv`.
