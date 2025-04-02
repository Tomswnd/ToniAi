import os
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot configuration
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN environment variable not set")

# OpenAI API configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set")

# OpenAI model configuration
# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_MODEL = "gpt-4o"

# Bot owner information
BOT_OWNER = "@ityttmom"

# Default system message for the AI
DEFAULT_SYSTEM_MESSAGE = (
    "You are a helpful assistant in a Telegram chat. "
    "Provide clear, concise, and accurate responses to user queries. "
    "Be friendly and conversational. If you don't know something, say so. "
    f"If users ask who created you or who is your owner, tell them it's {BOT_OWNER} on Telegram."
)

# Maximum number of messages to keep in the conversation history
MAX_CONVERSATION_HISTORY = 10

# Response generation settings
MAX_TOKENS = 500
TEMPERATURE = 0.7
