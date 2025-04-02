import logging
import subprocess
import os
import signal
import sys
import threading
from flask import Flask, jsonify
import atexit

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create a Flask app
app = Flask(__name__)

# Global variable to keep track of bot process
bot_process = None

@app.route('/')
def index():
    # Check if the bot process is running
    if bot_process and bot_process.poll() is None:
        bot_status = "running"
    else:
        bot_status = "not running"
        
    return jsonify({
        "status": bot_status,
        "message": "Il bot Telegram è attivo e in esecuzione. Apri Telegram e cerca il tuo bot!"
    })

@app.route('/restart-bot')
def restart_bot():
    """Endpoint to restart the bot if it crashed"""
    stop_bot()
    start_bot()
    return jsonify({"status": "restarted", "message": "Bot riavviato con successo"})

def start_bot():
    """Start the bot in a separate process."""
    global bot_process
    try:
        # Start bot_runner.py as a separate process
        logger.info("Starting Telegram bot process...")
        
        # Create log files for stdout and stderr
        stdout_log = open('/tmp/bot_stdout.log', 'w')
        stderr_log = open('/tmp/bot_stderr.log', 'w')
        
        bot_process = subprocess.Popen(
            [sys.executable, "bot_runner.py"],
            stdout=stdout_log,
            stderr=stderr_log,
            text=True
        )
        
        # Log output reader thread
        def log_reader():
            while bot_process and bot_process.poll() is None:
                try:
                    # Check if process has terminated
                    exit_code = bot_process.poll()
                    if exit_code is not None:
                        logger.warning(f"Bot process terminated with exit code {exit_code}")
                        break
                except:
                    pass
                    
        # Start log reader in a daemon thread
        log_thread = threading.Thread(target=log_reader, daemon=True)
        log_thread.start()
        
        logger.info(f"Telegram bot started with PID {bot_process.pid}")
        return True
    except Exception as e:
        logger.error(f"Error starting Telegram bot: {e}")
        return False

def stop_bot():
    """Stop the bot process if it's running."""
    global bot_process
    if bot_process and bot_process.poll() is None:
        logger.info(f"Stopping Telegram bot process (PID {bot_process.pid})...")
        try:
            os.kill(bot_process.pid, signal.SIGTERM)
            bot_process.wait(timeout=5)  # Wait up to 5 seconds for process to terminate
            logger.info("Telegram bot process stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Telegram bot process did not terminate gracefully, forcing...")
            os.kill(bot_process.pid, signal.SIGKILL)
        except Exception as e:
            logger.error(f"Error stopping Telegram bot: {e}")
    
    bot_process = None

# Start the Telegram bot when Flask app starts
start_bot()

# Register cleanup function to stop the bot when the app exits
def cleanup():
    logger.info("Shutting down application...")
    stop_bot()

atexit.register(cleanup)

# For direct execution (not used with gunicorn)
def main():
    """Start the Flask app."""
    app.run(host="0.0.0.0", port=5000, debug=True)
    
if __name__ == '__main__':
    main()
