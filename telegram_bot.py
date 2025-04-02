import telebot
import logging
from config import TELEGRAM_TOKEN
from openai_handler import OpenAIHandler

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI handler
openai_handler = OpenAIHandler()

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    """Send a message when the command /start is issued."""
    user_first_name = message.from_user.first_name
    welcome_message = (
        f"Ciao {user_first_name}! 👋\n\n"
        "Sono un bot alimentato da intelligenza artificiale utilizzando il modello GPT-4o di OpenAI.\n\n"
        "Puoi chiedermi qualsiasi cosa e cercherò di aiutarti nel migliore dei modi.\n\n"
        "Usa /reset per cancellare la cronologia della conversazione e iniziare una nuova chat.\n"
        "Usa /help per vedere l'elenco dei comandi disponibili."
    )
    bot.reply_to(message, welcome_message)

@bot.message_handler(commands=['help'])
def help_command(message):
    """Send a message when the command /help is issued."""
    help_message = (
        "Ecco i comandi disponibili:\n\n"
        "/start - Inizia una conversazione con il bot\n"
        "/help - Mostra questa lista di comandi\n"
        "/reset - Cancella la cronologia della conversazione e inizia una nuova chat\n\n"
        "Puoi semplicemente scrivermi un messaggio e io risponderò!"
    )
    bot.reply_to(message, help_message)

@bot.message_handler(commands=['reset'])
def reset_command(message):
    """Reset the conversation history for a user."""
    user_id = message.from_user.id
    response = openai_handler.reset_conversation(user_id)
    bot.reply_to(message, response)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Handle incoming messages and generate responses."""
    user_id = message.from_user.id
    message_text = message.text
    
    # Send typing action to indicate the bot is processing
    bot.send_chat_action(message.chat.id, 'typing')
    
    logger.info(f"Received message from user {user_id}: {message_text}")
    
    try:
        # Generate response using OpenAI
        response = openai_handler.generate_response(user_id, message_text)
        
        # Send the response back to the user
        bot.reply_to(message, response)
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        bot.reply_to(
            message,
            "Mi dispiace, ma ho riscontrato un problema nell'elaborare la tua richiesta. "
            "Riprova più tardi o resetta la conversazione con /reset."
        )

def run_bot():
    """Run the bot synchronously."""
    logger.info("Starting Telegram bot...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    logger.info("Bot polling stopped")
