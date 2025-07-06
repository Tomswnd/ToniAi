import logging
import subprocess
import os
import signal
import sys
import threading
import requests
import time
import datetime
import secrets
from flask import Flask, jsonify, render_template, make_response, request, redirect, url_for, session
import atexit
from openai import OpenAI
import os
import tempfile

from config import BOT_OWNER

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")
BOT_OWNER = "@ityttmom"

from chat_logger import chat_logger

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create a Flask app
app = Flask(__name__)
# Configurazione della sessione (necessaria per l'autenticazione)
app.secret_key = secrets.token_hex(16)

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
            model="gpt-4o-mini",
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
                            
                            <div class="text-center mt-3">
                                <a href="/admin" class="btn btn-outline-info">Area Amministrativa</a>
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
                                <div class="alert alert-secondary mt-3">
                                    <p class="mb-0">Per mantenere il bot attivo 24/7, consulta <a href="/keep-alive-info" class="alert-link">questa guida</a></p>
                                </div>
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
        # stdout_log = open('/tmp/bot_stdout.log', 'w')
        # stderr_log = open('/tmp/bot_stderr.log', 'w')
        # Per windows locale
        # stdout_log = open('bot_stdout.log', 'w')
        # stderr_log = open('bot_stderr.log', 'w')

        # Per render
        log_dir = tempfile.gettempdir()
        stdout_log = open(os.path.join(log_dir, 'bot_stdout.log'), 'w')
        stderr_log = open(os.path.join(log_dir, 'bot_stderr.log'), 'w')

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

# Health check e riavvio automatico del bot
def check_bot_health():
    """Controlla lo stato del bot e lo riavvia se necessario."""
    global bot_process

    # Se il processo non esiste o è terminato, riavvialo
    if bot_process is None or bot_process.poll() is not None:
        logger.warning("Bot non in esecuzione, riavvio automatico...")
        stop_bot()  # Per sicurezza, fermalo in ogni caso
        start_bot()
        return False
    return True

# Endpoint per la funzionalità di "pinging" per mantenere attiva l'applicazione
@app.route('/ping')
def ping():
    """Endpoint che può essere chiamato periodicamente per mantenere l'applicazione attiva"""
    # Controlla e riavvia il bot se necessario
    is_running = check_bot_health()

    # Restituisci lo stato del bot
    status = "up" if is_running else "restarted"
    return jsonify({"status": status, "timestamp": str(datetime.datetime.now())})

@app.route('/keep-alive-info')
def keep_alive_info():
    """Pagina informativa sul sistema di keep-alive"""
    # replit_url = os.environ.get('REPLIT_DB_URL', '').split('//')[1].split('.')[0]
    # if replit_url:
    #     ping_url = f"https://{replit_url}.repl.co/ping"
    # else:
    #     ping_url = "http://localhost:5000/ping"
    # per windows
    # ping_url = "http://localhost:5000/ping"
    # Per render
    render_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
    ping_url = f"{render_url}/ping"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mantieni Vivo il Bot 24/7</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-5">
            <div class="row">
                <div class="col-md-8 mx-auto">
                    <div class="card">
                        <div class="card-header">
                            <h1 class="h3 text-center">Come Mantenere il Bot Attivo 24/7</h1>
                        </div>
                        <div class="card-body">
                            <div class="alert alert-info">
                                <p>Per mantenere il bot sempre attivo, abbiamo implementato diverse strategie:</p>
                                <ol>
                                    <li><strong>Auto-riavvio</strong>: Il bot si riavvia automaticamente se crasha</li>
                                    <li><strong>Controllo periodico</strong>: Un controllo di stato avviene ogni 5 minuti</li>
                                    <li><strong>Sistema di ping</strong>: Il bot si auto-pinga per rimanere attivo</li>
                                </ol>
                            </div>
                            
                            <div class="mt-4">
                                <h5>Per un'attività 24/7 con un servizio esterno:</h5>
                                <p>Usa un servizio di monitoraggio come <a href="https://uptimerobot.com/" target="_blank" class="text-info">UptimeRobot</a> (gratuito) per pingare questo URL ogni 5 minuti:</p>
                                <div class="input-group mb-3">
                                    <input type="text" class="form-control" value="{ping_url}" readonly>
                                    <button class="btn btn-outline-secondary" type="button" onclick="navigator.clipboard.writeText('{ping_url}')">Copia</button>
                                </div>
                                <p class="small text-muted">Questo manterrà l'applicazione sempre attiva su Replit, evitando che venga messa in sospensione per inattività.</p>
                            </div>
                            
                            <div class="mt-4">
                                <h5>Istruzioni per UptimeRobot:</h5>
                                <ol>
                                    <li>Crea un account gratuito su <a href="https://uptimerobot.com/" target="_blank" class="text-info">UptimeRobot</a></li>
                                    <li>Aggiungi un nuovo "Monitor" di tipo HTTP(s)</li>
                                    <li>Inserisci il nome che preferisci</li>
                                    <li>Incolla l'URL sopra nel campo "URL (or IP)"</li>
                                    <li>Imposta l'intervallo a 5 minuti</li>
                                    <li>Salva il monitor</li>
                                </ol>
                            </div>
                            
                            <div class="text-center mt-4">
                                <a href="/" class="btn btn-primary">Torna alla Home</a>
                                <a href="{ping_url}" class="btn btn-secondary ms-2" target="_blank">Testa l'endpoint di ping</a>
                            </div>
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

# Funzione che avvia il thread di controllo salute del bot
def start_health_checker():
    """Avvia un thread che controlla periodicamente lo stato del bot"""
    def health_check_loop():
        while True:
            try:
                check_bot_health()
            except Exception as e:
                logger.error(f"Errore durante il controllo salute del bot: {e}")

            # Controlla ogni 5 minuti
            time.sleep(300)

    # Avvia il thread di controllo salute
    health_thread = threading.Thread(target=health_check_loop, daemon=True)
    health_thread.start()
    logger.info("Thread di controllo salute del bot avviato")

# Importa e inizializza il sistema di keep-alive
from keep_alive import init_keep_alive

# Start the Telegram bot when Flask app starts
start_bot()

# Avvia il thread di controllo salute del bot
start_health_checker()

# Inizializza il sistema di keep-alive (ping ogni 5 minuti)
keep_alive = init_keep_alive(interval=300)

# Register cleanup function to stop the bot when the app exits
def cleanup():
    logger.info("Shutting down application...")
    stop_bot()
    # Il keep-alive è un daemon thread, si fermerà automaticamente

atexit.register(cleanup)

# For direct execution (not used with gunicorn)
# Funzioni per la visualizzazione e gestione delle chat
@app.route('/admin')
def admin_login():
    """Pagina di login per l'area amministrativa"""
    html_content = """
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-5">
            <div class="row">
                <div class="col-md-6 mx-auto">
                    <div class="card">
                        <div class="card-header">
                            <h2 class="text-center">Accesso Area Amministrativa</h2>
                        </div>
                        <div class="card-body">
                            <form action="/admin/login" method="post">
                                <div class="mb-3">
                                    <label for="password" class="form-label">Password</label>
                                    <input type="password" class="form-control" id="password" name="password" required>
                                </div>
                                <div class="text-center">
                                    <button type="submit" class="btn btn-primary">Accedi</button>
                                </div>
                            </form>
                        </div>
                        <div class="card-footer text-center">
                            <small>Accesso riservato all'amministratore del bot</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/admin/login', methods=['POST'])
def admin_login_check():
    """Verifica le credenziali di accesso"""
    password = request.form.get('password')

    if password == ADMIN_PASSWORD:
        # Imposta la sessione come autenticata
        session['admin_authenticated'] = True
        # Redirect to admin panel
        return redirect('/admin/chats')
    else:
        html_content = """
        <!DOCTYPE html>
        <html lang="it" data-bs-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Accesso Negato</title>
            <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
            <meta http-equiv="refresh" content="3;url=/admin" />
        </head>
        <body>
            <div class="container py-5 text-center">
                <div class="alert alert-danger">
                    <h4>Password errata!</h4>
                    <p>Verrai reindirizzato alla pagina di login...</p>
                </div>
            </div>
        </body>
        </html>
        """

        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html'
        return response

@app.route('/admin/chats')
def admin_chats():
    """Pagina per visualizzare le chat degli utenti"""
    # Verifica che l'utente sia autenticato tramite la sessione
    if not session.get('admin_authenticated'):
        return redirect('/admin')

    # Ottieni l'elenco degli utenti
    users = chat_logger.get_user_info()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gestione Chat</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container py-4">
            <div class="row mb-4">
                <div class="col">
                    <h1 class="text-center">Pannello Amministrativo Chat</h1>
                    <p class="text-center text-muted">Visualizza le conversazioni degli utenti con il bot</p>
                </div>
            </div>
            
            <div class="row mb-4">
                <div class="col">
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h4 class="mb-0">Utenti ({len(users)})</h4>
                            <div>
                                <a href="/admin/logout" class="btn btn-sm btn-outline-danger">Logout</a>
                                <a href="/" class="btn btn-sm btn-outline-secondary ms-2">Torna alla Home</a>
                            </div>
                        </div>
                        <div class="card-body p-0">
    """

    if users:
        html_content += """
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead>
                                        <tr>
                                            <th>ID Utente</th>
                                            <th>Username</th>
                                            <th>Nome</th>
                                            <th>Ultimo Messaggio</th>
                                            <th>Messaggi</th>
                                            <th>Azioni</th>
                                        </tr>
                                    </thead>
                                    <tbody>
        """

        for user in users:
            user_id = user.get('user_id', '')
            username = user.get('username', 'Nessun username')
            first_name = user.get('first_name', 'Nessun nome')
            last_message = user.get('last_message_time', '').split('T')[0]  # Solo la data
            message_count = user.get('message_count', 0)

            html_content += f"""
                                        <tr>
                                            <td>{user_id}</td>
                                            <td>{username}</td>
                                            <td>{first_name}</td>
                                            <td>{last_message}</td>
                                            <td>{message_count}</td>
                                            <td>
                                                <a href="/admin/chat/{user_id}" class="btn btn-sm btn-info">Visualizza</a>
                                            </td>
                                        </tr>
            """

        html_content += """
                                    </tbody>
                                </table>
                            </div>
        """
    else:
        html_content += """
                            <div class="alert alert-info m-3">
                                <p class="mb-0">Nessun utente ha ancora interagito con il bot.</p>
                            </div>
        """

    html_content += """
                        </div>
                        <div class="card-footer text-center">
                            <small>I messaggi vengono salvati nella directory 'chats/'</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/admin/chat/<int:user_id>')
def admin_view_chat(user_id):
    """Visualizza la chat di un utente specifico"""
    # Verifica che l'utente sia autenticato
    if not session.get('admin_authenticated'):
        return redirect('/admin')

    # Ottieni la chat dell'utente
    chats = chat_logger.get_user_chats(user_id)
    user_chat = chats.get(user_id, [])

    # Se la chat esiste, prendi il nome utente dal primo messaggio
    username = "Utente sconosciuto"
    first_name = "Utente"
    if user_chat and user_chat[0].get('username'):
        username = user_chat[0].get('username', 'Nessun username')
        first_name = user_chat[0].get('first_name', 'Nessun nome')

    html_content = f"""
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat con {username}</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <style>
            .message-container {{
                max-height: 70vh;
                overflow-y: auto;
            }}
            .user-message {{
                background-color: var(--bs-gray-800);
                border-radius: 1rem 1rem 0.3rem 1rem;
                padding: 1rem;
                margin-bottom: 1rem;
                max-width: 80%;
                align-self: flex-end;
            }}
            .bot-message {{
                background-color: var(--bs-gray-700);
                border-radius: 1rem 1rem 1rem 0.3rem;
                padding: 1rem;
                margin-bottom: 1rem;
                max-width: 80%;
                align-self: flex-start;
            }}
            .timestamp {{
                font-size: 0.8rem;
                color: var(--bs-gray-500);
                margin-top: 0.5rem;
            }}
        </style>
    </head>
    <body>
        <div class="container py-4">
            <div class="row mb-4">
                <div class="col">
                    <div class="d-flex justify-content-between align-items-center">
                        <h2>Chat con {username} ({first_name})</h2>
                        <div>
                            <a href="/admin/chats" class="btn btn-outline-secondary">Torna alla lista</a>
                            <a href="/" class="btn btn-outline-primary ms-2">Home</a>
                            <a href="/admin/logout" class="btn btn-outline-danger ms-2">Logout</a>
                        </div>
                    </div>
                    <p class="text-muted">ID Utente: {user_id} - Totale messaggi: {len(user_chat)}</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col">
                    <div class="card">
                        <div class="card-header">
                            <h4 class="mb-0">Cronologia Messaggi</h4>
                        </div>
                        <div class="card-body message-container">
    """

    if user_chat:
        html_content += """
                            <div class="d-flex flex-column">
        """

        for message in user_chat:
            timestamp = message.get('timestamp', '').replace('T', ' ').split('.')[0]  # Formatta la data
            user_message = message.get('user_message', '')
            bot_response = message.get('bot_response', '')

            html_content += f"""
                                <div class="user-message align-self-end">
                                    <div>{user_message}</div>
                                    <div class="timestamp">{timestamp}</div>
                                </div>
                                <div class="bot-message align-self-start">
                                    <div>{bot_response}</div>
                                    <div class="timestamp">{timestamp}</div>
                                </div>
            """

        html_content += """
                            </div>
        """
    else:
        html_content += """
                            <div class="alert alert-info">
                                <p class="mb-0">Nessun messaggio trovato per questo utente.</p>
                            </div>
        """

    html_content += """
                        </div>
                        <div class="card-footer text-center">
                            <small>Fine della conversazione</small>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // Scroll to bottom of messages on load
            document.addEventListener('DOMContentLoaded', function() {
                const messageContainer = document.querySelector('.message-container');
                messageContainer.scrollTop = messageContainer.scrollHeight;
            });
        </script>
    </body>
    </html>
    """

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

@app.route('/admin/logout')
def admin_logout():
    """Effettua il logout dall'area amministrativa"""
    # Rimuovi la sessione di autenticazione
    session.pop('admin_authenticated', None)

    # Redirect alla pagina di login con messaggio di successo
    html_content = """
    <!DOCTYPE html>
    <html lang="it" data-bs-theme="dark">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Logout effettuato</title>
        <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
        <meta http-equiv="refresh" content="2;url=/" />
    </head>
    <body>
        <div class="container py-5 text-center">
            <div class="alert alert-success">
                <h4>Logout effettuato con successo</h4>
                <p>Stai per essere reindirizzato alla home page...</p>
            </div>
        </div>
    </body>
    </html>
    """

    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

def main():
    # Per windows
    # app.run(host="0.0.0.0", port=5000, debug=True)
    # Per render
    port = int(os.environ.get('PORT', 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

if __name__ == '__main__':
    main()