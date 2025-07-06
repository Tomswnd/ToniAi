"""
Modulo per mantenere vivo il servizio 24/7 su Render.
Render mantiene automaticamente i servizi attivi, quindi questo modulo è semplificato.
"""
import os
import threading
import time
import requests
import logging

logger = logging.getLogger(__name__)

class KeepAlive:
    """Classe per mantenere vivo il servizio su Render utilizzando auto-ping"""
    def __init__(self, interval=5*60):  # 5 minuti di default (più frequente per Render)
        """
        Inizializza il servizio di keep-alive

        Args:
            interval: intervallo in secondi tra i ping
        """
        self.interval = interval
        self.running = False
        self.thread = None

        # Ottieni l'URL del servizio Render
        self.render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
        if self.render_url:
            self.ping_url = f"{self.render_url}/ping"
        else:
            # Fallback per sviluppo locale
            port = os.environ.get('PORT', '5000')
            self.ping_url = f"http://localhost:{port}/ping"
            logger.warning(f"Nessun URL Render trovato, utilizzo locale: {self.ping_url}")

    def _ping_server(self):
        """Invia una richiesta al nostro endpoint di ping"""
        try:
            response = requests.get(self.ping_url, timeout=30)
            if response.status_code == 200:
                logger.info(f"Ping riuscito: {response.json()}")
            else:
                logger.warning(f"Ping fallito con codice {response.status_code}")
        except Exception as e:
            logger.error(f"Errore durante il ping: {e}")

    def _keep_alive_loop(self):
        """Loop che invia periodicamente ping al server"""
        while self.running:
            self._ping_server()
            time.sleep(self.interval)

    def start(self):
        """Avvia il thread di keep-alive"""
        if self.thread and self.thread.is_alive():
            logger.info("Il servizio di keep-alive è già in esecuzione")
            return

        logger.info(f"Avvio servizio di keep-alive su Render, ping a {self.ping_url} ogni {self.interval} secondi")
        self.running = True
        self.thread = threading.Thread(target=self._keep_alive_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Ferma il thread di keep-alive"""
        logger.info("Arresto servizio di keep-alive")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

# Funzione di utilità per iniziare il servizio
def init_keep_alive(interval=5*60):
    """Inizializza e avvia il servizio di keep-alive"""
    keep_alive = KeepAlive(interval)
    keep_alive.start()
    return keep_alive

# Funzione per ottenere la porta corretta per Render
def get_render_port():
    """Ottiene la porta da utilizzare su Render"""
    return int(os.environ.get('PORT', 5000))

# Funzione per ottenere l'host corretto per Render
def get_render_host():
    """Ottiene l'host da utilizzare su Render"""
    return '0.0.0.0'  # Render richiede di ascoltare su tutte le interfacce