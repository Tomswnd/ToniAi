from telegram_bot import create_application
import logging
from config import TELEGRAM_TOKEN

def main():
    """Start the bot."""
    # Get the application instance
    application = create_application()
    
    # Run the bot until the user presses Ctrl-C
    logging.info("Starting bot...")
    application.run_polling()
    
if __name__ == '__main__':
    main()
