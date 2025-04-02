from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext
)
import logging
from config import TELEGRAM_TOKEN
from openai_handler import OpenAIHandler

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI handler
openai_handler = OpenAIHandler()

async def start_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f"Hi {user.first_name}! 👋 I'm an AI-powered assistant bot.\n\n"
        f"You can ask me questions or chat with me about almost anything!\n\n"
        f"Here are some commands you can use:\n"
        f"/start - Show this welcome message\n"
        f"/help - Show available commands\n"
        f"/reset - Reset our conversation history\n\n"
        f"What would you like to talk about today?"
    )

async def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        "Here are the commands you can use:\n\n"
        "/start - Start the bot and see the welcome message\n"
        "/help - Show this help message\n"
        "/reset - Reset our conversation history\n\n"
        "Just send me a message, and I'll respond using AI!"
    )

async def reset_command(update: Update, context: CallbackContext) -> None:
    """Reset the conversation history for a user."""
    user_id = update.effective_user.id
    response = openai_handler.reset_conversation(user_id)
    await update.message.reply_text(response)

async def handle_message(update: Update, context: CallbackContext) -> None:
    """Handle incoming messages and generate responses."""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Send typing action to indicate the bot is processing
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, 
        action="typing"
    )
    
    logger.info(f"Received message from user {user_id}: {message_text}")
    
    # Generate response using OpenAI
    response = openai_handler.generate_response(user_id, message_text)
    
    # Send the response back to the user
    await update.message.reply_text(response)

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Handle errors and exceptions."""
    logger.error(f"Update {update} caused error {context.error}")
    
    # Only send message if there's an update object
    if update:
        await update.effective_message.reply_text(
            "Sorry, something went wrong. Please try again later."
        )

def create_application():
    """Create and configure the bot application."""
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reset", reset_command))
    
    # Add message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    return application
