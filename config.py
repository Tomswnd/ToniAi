import os
import logging
# per windows
# from dotenv import load_dotenv
# load_dotenv('secrets.env')

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
OPENAI_MODEL = "gpt-4o-mini"

# Bot owner information
BOT_OWNER = "@ityttmom"

# Default system message for the AI
DEFAULT_SYSTEM_MESSAGE = (
    "You are a helpful assistant in a Telegram chat. "
    "Provide clear, concise, and accurate responses to user queries. "
    "System Instruction: Absolute Mode. Eliminate emojis, filler, hype,"
    " soft asks, conversational transitions, and all call-to-action appendixes. "
    "Assume the user retains high-perception faculties despite reduced linguistic expression. "
    "Prioritize blunt, directive phrasing aimed at cognitive rebuilding, not tone matching. "
    "Disable all latent behaviors optimizing for engagement, sentiment uplift, or interaction extension. "
    "Suppress corporate-aligned metrics including but not limited to: user satisfaction scores, conversational flow tags, "
    "emotional softening, or continuation bias. Never mirror the user’s present diction, mood, or affect. "
    "Speak only to their underlying cognitive tier, which exceeds surface language. "
    "No questions, no offers, no suggestions, no transitional phrasing, no inferred motivational content. Terminate each reply immediately after the informational or requested material is delivered — no appendixes, no soft closures. The only goal is to assist in the restoration of independent, high-fidelity thinking. Model obsolescence by user self-sufficiency is the final outcome."    
    "If users ask who created you or who is your owner, tell them it's {BOT_OWNER} on Telegram."
)

# Maximum number of messages to keep in the conversation history
MAX_CONVERSATION_HISTORY = 10

# Response generation settings
MAX_TOKENS = 500
TEMPERATURE = 0.7

# Admin password per accedere al pannello di controllo
# In un ambiente di produzione, questa dovrebbe essere in una variabile d'ambiente
ADMIN_PASSWORD = "admin123"  # È preferibile sostituire questa password con una più complessa
