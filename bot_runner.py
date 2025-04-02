#!/usr/bin/env python3
import logging
from telegram_bot import run_bot
from config import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        logger.info("Starting bot runner...")
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Bot error: {e}")