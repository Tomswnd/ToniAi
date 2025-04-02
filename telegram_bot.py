import telebot
import logging
from config import TELEGRAM_TOKEN, BOT_OWNER
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
        f"Sono stato creato da {BOT_OWNER} su Telegram.\n\n"
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
        "Puoi semplicemente scrivermi un messaggio e io risponderò!\n\n"
        f"Questo bot è stato sviluppato da {BOT_OWNER} su Telegram."
    )
    bot.reply_to(message, help_message)

@bot.message_handler(commands=['reset'])
def reset_command(message):
    """Reset the conversation history for a user."""
    user_id = message.from_user.id
    response = openai_handler.reset_conversation(user_id)
    bot.reply_to(message, response)

def get_fallback_response(message_text):
    """Provide basic responses for common queries when OpenAI is not available"""
    message_lower = message_text.lower()
    
    # Dictionary of common queries and their responses
    fallback_responses = {
        "ciao": "Ciao! Come posso aiutarti oggi?",
        "come stai": "Sto bene, grazie! Sono qui per aiutarti.",
        "grazie": "Prego! Sono felice di esserti stato utile.",
        "chi sei": f"Sono un bot di assistenza creato da {BOT_OWNER} su Telegram per aiutarti con le tue domande.",
        "chi ti ha creato": f"Sono stato creato da {BOT_OWNER} su Telegram.",
        "chi è il tuo proprietario": f"Il mio proprietario è {BOT_OWNER} su Telegram.",
        "cosa puoi fare": "Posso rispondere alle tue domande su vari argomenti quando l'intelligenza artificiale è disponibile. Al momento sto operando in modalità limitata.",
        "aiuto": "Usa /help per vedere la lista dei comandi disponibili."
    }
    
    # Check if the message matches any key in the dictionary
    for key, response in fallback_responses.items():
        if key in message_lower:
            return response
    
    # Default response if no match is found
    return "Mi dispiace, al momento non posso generare risposte personalizzate a causa di limitazioni tecniche. Prova a usare /help per vedere i comandi disponibili o riprova più tardi."

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
        
        # Use fallback response system when OpenAI is not available
        fallback_response = get_fallback_response(message_text)
        bot.reply_to(message, fallback_response)

def run_bot():
    """Run the bot synchronously."""
    logger.info("Starting Telegram bot...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    logger.info("Bot polling stopped")
