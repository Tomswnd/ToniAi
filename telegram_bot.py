import telebot
import logging
import datetime
from config import TELEGRAM_TOKEN, BOT_OWNER, OPENAI_MODEL
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
    # Log dettagliato per i comandi
    logger.info(f"Comando /start ricevuto: {message.text}")
    
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    logger.info(f"Comando in gruppo: {is_group_chat}")
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai' o è di tipo menzione
    if is_group_chat:
        # Per i comandi nei gruppi, controlla se il testo completo inizia con 'toniai'
        message_text = message.text if message.text else ""
        logger.info(f"Testo comando in gruppo: '{message_text}'")
        
        # Controlla anche se è un comando diretto al bot tramite @nome_bot
        if (not message_text.lower().startswith('toniai') and 
            not message_text.startswith('/start@')):
            logger.info(f"Comando ignorato in gruppo: '{message_text}'")
            return
    
    user_first_name = message.from_user.first_name
    welcome_message = (
        f"Ciao {user_first_name}! 👋\n\n"
        f"Sono un bot alimentato da intelligenza artificiale utilizzando il modello {OPENAI_MODEL} di OpenAI.\n\n"
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
            "toniai /help - Per vedere questa guida e altre informazioni"
        )
    else:
        welcome_message += (
            "Puoi chiedermi qualsiasi cosa e cercherò di aiutarti nel migliore dei modi.\n\n"
            "Usa /reset per cancellare la cronologia della conversazione e iniziare una nuova chat.\n"
            "Usa /help per vedere l'elenco dei comandi disponibili e informazioni sull'uso nei gruppi."
        )
    
    bot.reply_to(message, welcome_message)

@bot.message_handler(commands=['help'])
def help_command(message):
    """Send a message when the command /help is issued."""
    # Log dettagliato per i comandi
    logger.info(f"Comando /help ricevuto: {message.text}")
    
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    logger.info(f"Comando in gruppo: {is_group_chat}")
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai' o è di tipo menzione
    if is_group_chat:
        # Per i comandi nei gruppi, controlla se il testo completo inizia con 'toniai'
        message_text = message.text if message.text else ""
        logger.info(f"Testo comando in gruppo: '{message_text}'")
        
        # Controlla anche se è un comando diretto al bot tramite @nome_bot
        if (not message_text.lower().startswith('toniai') and 
            not message_text.startswith('/help@')):
            logger.info(f"Comando ignorato in gruppo: '{message_text}'")
            return
    
    # Ottieni il nome utente del bot
    bot_info = bot.get_me()
    bot_username = bot_info.username
    
    # Prepara il messaggio di aiuto in base al tipo di chat
    if is_group_chat:
        help_message = (
            "Ecco come utilizzarmi in questa chat di gruppo:\n\n"
            "Inizia sempre il tuo messaggio con 'toniai' per farmi rispondere.\n\n"
            "Comandi disponibili:\n"
            "toniai /start - Mostra messaggio di benvenuto\n"
            "toniai /help - Mostra questa lista di comandi\n"
            "toniai /reset - Cancella la cronologia della conversazione\n\n"
            "Puoi anche usare: /comando@" + bot_username + "\n\n"
            "Esempio: toniai raccontami una storia\n\n"
            f"Questo bot utilizza il modello AI: {OPENAI_MODEL}\n"
            f"Sviluppato da {BOT_OWNER} su Telegram."
        )
    else:
        help_message = (
            "Ecco i comandi disponibili:\n\n"
            "/start - Inizia una conversazione con il bot\n"
            "/help - Mostra questa lista di comandi\n"
            "/reset - Cancella la cronologia della conversazione\n\n"
            "Puoi semplicemente scrivermi un messaggio e io risponderò!\n\n"
            "Nei gruppi, inizia sempre i messaggi con 'toniai' per farmi rispondere.\n\n"
            f"Questo bot utilizza il modello AI: {OPENAI_MODEL}\n"
            f"Sviluppato da {BOT_OWNER} su Telegram."
        )
    
    bot.reply_to(message, help_message)

@bot.message_handler(commands=['reset'])
def reset_command(message):
    """Reset the conversation history for a user."""
    # Log dettagliato per i comandi
    logger.info(f"Comando /reset ricevuto: {message.text}")
    
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    logger.info(f"Comando in gruppo: {is_group_chat}")
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai' o è di tipo menzione
    if is_group_chat:
        # Per i comandi nei gruppi, controlla se il testo completo inizia con 'toniai'
        message_text = message.text if message.text else ""
        logger.info(f"Testo comando in gruppo: '{message_text}'")
        
        # Controlla anche se è un comando diretto al bot tramite @nome_bot
        if (not message_text.lower().startswith('toniai') and 
            not message_text.startswith('/reset@')):
            logger.info(f"Comando ignorato in gruppo: '{message_text}'")
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
    # Log dettagliato per il debugging nei gruppi
    logger.info(f"Ricevuto messaggio: {message}")
    logger.info(f"Tipo di chat: {message.chat.type}")
    
    user_id = message.from_user.id
    chat_id = message.chat.id
    message_text = message.text if message.text else ""
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Log dettagliato del testo del messaggio
    logger.info(f"Testo messaggio: '{message_text}'")
    
    # Controlla se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    logger.info(f"È una chat di gruppo: {is_group_chat}")
    
    # In una chat di gruppo, rispondi solo se il messaggio inizia con "toniai" (case insensitive)
    if is_group_chat:
        # Verifica se il messaggio è vuoto o non inizia con "toniai"
        if not message_text:
            logger.info("Messaggio vuoto in gruppo, ignoro")
            return
            
        logger.info(f"Controllo se '{message_text}' inizia con 'toniai' (case insensitive)")
        if not message_text.lower().startswith("toniai"):
            # Se non inizia con "toniai", ignora il messaggio
            logger.info(f"Ignoro messaggio in gruppo che non inizia con 'toniai': '{message_text}'")
            return
        
        logger.info("Il messaggio inizia con 'toniai', procedo all'elaborazione")
        
        # Trova la posizione di "toniai" (case insensitive) ed estrai il resto del messaggio
        toniai_pos = message_text.lower().find("toniai")
        actual_message = message_text[toniai_pos + len("toniai"):].strip()
        logger.info(f"Messaggio dopo la rimozione di 'toniai': '{actual_message}'")
        
        if not actual_message:
            # Se il messaggio è solo "toniai", chiedi come posso aiutare
            logger.info("Il messaggio contiene solo 'toniai', invio risposta predefinita")
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



@bot.message_handler(commands=['debug'])
def debug_command(message):
    """Comando per debugging del bot - riservato agli sviluppatori"""
    # Log del comando di debug
    logger.info(f"Comando /debug ricevuto da {message.from_user.username} (ID: {message.from_user.id})")
    
    # Verifica se il messaggio è in una chat di gruppo
    is_group_chat = message.chat.type in ['group', 'supergroup']
    logger.info(f"Comando debug in gruppo: {is_group_chat}")
    
    # Nei gruppi, rispondi solo se il comando inizia con 'toniai' o è di tipo menzione
    if is_group_chat:
        message_text = message.text if message.text else ""
        logger.info(f"Testo comando debug in gruppo: '{message_text}'")
        
        # Controlla anche se è un comando diretto al bot tramite @nome_bot
        if (not message_text.lower().startswith('toniai') and 
            not message_text.startswith('/debug@')):
            logger.info(f"Comando debug ignorato in gruppo: '{message_text}'")
            return
    
    # Solo il proprietario del bot può usare questo comando
    # Controlliamo sia per ID che per username
    is_owner = (str(message.from_user.id) == "713164389" or  # ID numerico del proprietario
                message.from_user.username == "ityttmom")    # Username del proprietario
    
    if not is_owner:
        logger.info(f"Tentativo di accesso al comando debug da utente non autorizzato: {message.from_user.username}")
        bot.reply_to(message, "Comando riservato allo sviluppatore del bot.")
        return
        
    logger.info("Accesso al debug autorizzato, generazione informazioni di debug")
    
    # Informazioni di debug
    bot_info = bot.get_me()
    bot_username = bot_info.username
    
    debug_message = f"""
🔍 *Informazioni di Debug del Bot*

👤 *Bot Username:* @{bot_username}
⚙️ *Versione:* 1.0.2 (Debug patch 4)
🕒 *Ultimo riavvio:* {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🤖 *Modello AI:* {OPENAI_MODEL}

*Stati interni:*
- Chat ID attuale: `{message.chat.id}`
- Tipo di chat: `{message.chat.type}`
- User ID: `{message.from_user.id}`
- Username: `{message.from_user.username}`

*Formato comandi nei gruppi:*
Per usare comandi in gruppo puoi usare:
1. `toniai /comando`
2. `/comando@{bot_username}`

*Esempio funzionamento in gruppi:*
• `toniai ciao` → risponde al messaggio
• `toniai` → chiede cosa può fare
• `toniai /reset` → cancella la conversazione
• `/reset@{bot_username}` → cancella la conversazione
• Messaggio senza "toniai" → viene ignorato

*Log estesi:* Attivati
*Supporto menzioni:* Attivato
*Diagnostica gruppi:* Attivata

*Per assistenza contatta {BOT_OWNER}*
"""
    
    bot.reply_to(message, debug_message, parse_mode="Markdown")

def run_bot():
    """Run the bot synchronously."""
    logger.info("Starting Telegram bot...")
    
    try:
        # Ottieni e logga informazioni sul bot
        me = bot.get_me()
        logger.info(f"Bot avviato correttamente. Username: @{me.username}, ID: {me.id}")
        
        # Avvia il polling in ascolto dei messaggi
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Errore nell'avvio del bot: {e}")
    
    logger.info("Bot polling stopped")
