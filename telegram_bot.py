import telebot
import logging
from config import TELEGRAM_TOKEN, BOT_OWNER
from openai_handler import OpenAIHandler
from chat_logger import chat_logger

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the OpenAI handler
openai_handler = OpenAIHandler()

# Initialize the bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start_command(message):
    """Send a message when the command /start is issued."""
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai'
    if is_group_chat:
        # Per i comandi nei gruppi, controlla se il testo completo inizia con 'toniai'
        message_text = message.text.lower()
        if not message_text.startswith('toniai'):
            return
    
    user_first_name = message.from_user.first_name
    welcome_message = (
        f"Ciao {user_first_name}! 👋\n\n"
        "Sono un bot alimentato da intelligenza artificiale utilizzando il modello GPT-4o di OpenAI.\n\n"
        f"Sono stato creato da {BOT_OWNER} su Telegram.\n\n"
    )
    
    # Aggiungi istruzioni specifiche in base al tipo di chat
    if is_group_chat:
        welcome_message += (
            "In questa chat di gruppo risponderò solo ai messaggi che iniziano con 'toniai'.\n\n"
            "Esempi:\n"
            "toniai raccontami una storia\n"
            "toniai qual è la capitale dell'Italia?\n\n"
            "Puoi anche usare:\n"
            "toniai /reset - Per cancellare la cronologia della conversazione\n"
            "toniai /help - Per vedere questa guida"
        )
    else:
        welcome_message += (
            "Puoi chiedermi qualsiasi cosa e cercherò di aiutarti nel migliore dei modi.\n\n"
            "Usa /reset per cancellare la cronologia della conversazione e iniziare una nuova chat.\n"
            "Usa /help per vedere l'elenco dei comandi disponibili."
        )
    
    bot.reply_to(message, welcome_message)

@bot.message_handler(commands=['help'])
def help_command(message):
    """Send a message when the command /help is issued."""
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai'
    if is_group_chat:
        # Per i comandi nei gruppi, controlla se il testo completo inizia con 'toniai'
        message_text = message.text.lower()
        if not message_text.startswith('toniai'):
            return
    
    # Prepara il messaggio di aiuto in base al tipo di chat
    if is_group_chat:
        help_message = (
            "Ecco come utilizzarmi in questa chat di gruppo:\n\n"
            "Inizia sempre il tuo messaggio con 'toniai' per farmi rispondere.\n\n"
            "Comandi disponibili:\n"
            "toniai /start - Mostra messaggio di benvenuto\n"
            "toniai /help - Mostra questa lista di comandi\n"
            "toniai /reset - Cancella la cronologia della conversazione\n\n"
            "Esempio: toniai raccontami una storia\n\n"
            f"Questo bot è stato sviluppato da {BOT_OWNER} su Telegram."
        )
    else:
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
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai'
    if is_group_chat:
        # Per i comandi nei gruppi, controlla se il testo completo inizia con 'toniai'
        message_text = message.text.lower()
        if not message_text.startswith('toniai'):
            return
    
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
    """
    Handle incoming messages and generate responses.
    In group chats, only respond when the message starts with 'toniai'.
    In private chats, respond to all messages.
    """
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_text = message.text
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Controlla se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    
    # In una chat di gruppo, rispondi solo se il messaggio inizia con "toniai"
    if is_group_chat:
        words = message_text.split()
        if not words or words[0].lower() != "toniai":
            # Se non inizia con "toniai", ignora il messaggio
            logger.info(f"Ignoro messaggio in gruppo che non inizia con 'toniai': {message_text}")
            return
        
        # Rimuovi "toniai" dal messaggio per l'elaborazione
        actual_message = message_text[len("toniai"):].strip()
        if not actual_message:
            # Se il messaggio è solo "toniai", chiedi come posso aiutare
            bot.reply_to(message, "Ciao! Sono qui per aiutarti. Cosa vorresti sapere?")
            return
        
        message_text = actual_message
    
    # Send typing action to indicate the bot is processing
    bot.send_chat_action(chat_id, 'typing')
    
    logger.info(f"Elaborazione messaggio da utente {user_id}: {message_text}")
    
    try:
        # Generate response using OpenAI
        response = openai_handler.generate_response(user_id, message_text)
        
        # Send the response back to the user
        bot.reply_to(message, response)
        
        # Log the message and response
        chat_logger.log_message(
            user_id=user_id,
            user_message=message_text,
            bot_response=response,
            username=username,
            first_name=first_name
        )
    except Exception as e:
        logger.error(f"Error generating response: {e}")
        
        # Use fallback response system when OpenAI is not available
        fallback_response = get_fallback_response(message_text)
        bot.reply_to(message, fallback_response)
        
        # Log the message and fallback response
        chat_logger.log_message(
            user_id=user_id,
            user_message=message_text,
            bot_response=fallback_response,
            username=username,
            first_name=first_name
        )

def run_bot():
    """Run the bot synchronously."""
    logger.info("Starting Telegram bot...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
    logger.info("Bot polling stopped")
