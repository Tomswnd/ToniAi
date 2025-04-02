import logging
import subprocess
import os
import signal
import sys
import threading
import requests
from flask import Flask, jsonify, render_template, make_response
import atexit
from openai import OpenAI
from config import OPENAI_API_KEY, BOT_OWNER

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
    """Main page showing bot status and information"""
    # Check if the bot process is running
    if bot_process and bot_process.poll() is None:
        bot_status = "running"
        status_color = "success"
        status_text = "Attivo"
    else:
        bot_status = "not running"
        status_color = "danger"
        status_text = "Fermo"
    
    # Check OpenAI API status
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Send a minimal request to check API status
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_tokens=3
        )
        
        openai_status = "active"
        openai_status_color = "success"
        openai_status_text = "Attivo"
    except Exception as e:
        error_message = str(e)
        if "insufficient_quota" in error_message:
            openai_status = "quota_exceeded"
            openai_status_color = "warning"
            openai_status_text = "Quota superata"
        else:
            openai_status = "error"
            openai_status_color = "danger"
            openai_status_text = "Errore"
    
    # Create HTML response
    html_content = f"""
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Stato del Bot Telegram</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            .bot-status {{
                font-size: 1.2rem;
                margin-bottom: 1.5rem;
            }}
            .api-status {{
                font-size: 1.2rem;
                margin-bottom: 1.5rem;
            }}
            .commands {{
                margin-top: 2rem;
            }}
            .card {{
                margin-bottom: 1.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="container py-5">
            <div class="row">
                <div class="col-md-8 mx-auto">
                    <div class="card">
                        <div class="card-header">
                            <h1 class="display-5 text-center">Telegram Bot AI</h1>
                        </div>
                        <div class="card-body">
                            <div class="bot-status text-center">
                                <p>Stato del Bot: <span class="badge bg-{status_color}">{status_text}</span></p>
                                <button class="btn btn-primary" onclick="location.href='/restart-bot'">Riavvia Bot</button>
                            </div>
                            
                            <div class="api-status text-center">
                                <p>Stato API OpenAI: <span class="badge bg-{openai_status_color}">{openai_status_text}</span></p>
                                <button class="btn btn-secondary" onclick="location.href='/check-openai'">Controlla API</button>
                            </div>
                            
                            <hr>
                            
                            <div class="commands">
                                <h4>Comandi disponibili sul bot:</h4>
                                <ul class="list-group">
                                    <li class="list-group-item">/start - Inizia una conversazione con il bot</li>
                                    <li class="list-group-item">/help - Mostra la lista dei comandi disponibili</li>
                                    <li class="list-group-item">/reset - Cancella la cronologia della conversazione</li>
                                </ul>
                            </div>
                            
                            <div class="mt-4">
                                <h4>Come utilizzare:</h4>
                                <p>1. Apri Telegram e cerca il tuo bot</p>
                                <p>2. Invia un messaggio al bot per iniziare una conversazione</p>
                                <p>3. Il bot risponderà utilizzando l'intelligenza artificiale di OpenAI</p>
                            </div>
                        </div>
                        <div class="card-footer text-center">
                            <small>Bot sviluppato con Python, Flask e OpenAI</small><br>
                            <small>Proprietario: {BOT_OWNER} su Telegram</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/restart-bot')
def restart_bot():
    """Endpoint to restart the bot if it crashed"""
    stop_bot()
    start_bot()
    
    # Redirect to home page with success message
    html_content = """
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bot Riavviato</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <meta http-equiv="refresh" content="2;url=/" />
    </head>
    <body>
        <div class="container py-5 text-center">
            <div class="alert alert-success">
                <h4>Bot riavviato con successo!</h4>
                <p>Stai per essere reindirizzato alla home page...</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/check-openai')
def check_openai():
    """Check if OpenAI API is working correctly"""
    try:
        # Initialize OpenAI client with the API key
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Send a minimal request to check API status
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, are you working?"}
            ],
            max_tokens=5  # Minimal tokens to save quota
        )
        
        # If we get here, the API is working
        html_content = """
        <!DOCTYPE html>
        <html lang="it" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Stato API OpenAI</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <meta http-equiv="refresh" content="3;url=/" />
        </head>
        <body>
            <div class="container py-5 text-center">
                <div class="alert alert-success">
                    <h4>API OpenAI funzionante!</h4>
                    <p>L'API OpenAI è attiva e funzionante correttamente.</p>
                    <p>Stai per essere reindirizzato alla home page...</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response
    except Exception as e:
        error_message = str(e)
        
        if "insufficient_quota" in error_message:
            error_type = "Quota API superata"
            error_details = "La quota dell'API OpenAI è stata superata. È necessario aggiornare la chiave API."
        else:
            error_type = "Errore API"
            error_details = f"Errore nell'API OpenAI: {error_message}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Errore API OpenAI</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <meta http-equiv="refresh" content="5;url=/" />
        </head>
        <body>
            <div class="container py-5 text-center">
                <div class="alert alert-danger">
                    <h4>{error_type}</h4>
                    <p>{error_details}</p>
                    <p>Stai per essere reindirizzato alla home page...</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response

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
