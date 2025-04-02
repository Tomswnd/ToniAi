from telegram_bot import create_application
import logging
from config import TELEGRAM_TOKEN
from flask import Flask, render_template, jsonify
import threading

# Create a Flask app
app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "running",
        "message": "Il bot Telegram è attivo e in esecuzione. Apri Telegram e cerca il tuo bot!"
    })

def run_telegram_bot():
    """Start the bot in a separate thread."""
    # Get the application instance
    application = create_application()
    
    # Run the bot until the user presses Ctrl-C
    logging.info("Starting bot...")
    application.run_polling()

def main():
    """Start both the Flask app and the Telegram bot."""
    # Start the Telegram bot in a separate thread
    bot_thread = threading.Thread(target=run_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    logging.info("Telegram bot started in background thread")
    
if __name__ == '__main__':
    main()
