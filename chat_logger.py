"""
Modulo per la registrazione e gestione delle conversazioni degli utenti con il bot.
"""
import os
import json
import logging
import datetime
from typing import List, Dict, Any, Optional
from config import BOT_OWNER

logger = logging.getLogger(__name__)

# Directory per salvare i file delle conversazioni
CHATS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chats")

# Assicurati che la directory esista
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)
    logger.info(f"Creata directory per le chat: {CHATS_DIR}")


class ChatLogger:
    """Classe per registrare e gestire le conversazioni degli utenti con il bot."""

    def __init__(self):
        """Inizializza il logger delle chat."""
        self.ensure_chats_dir()

    @staticmethod
    def ensure_chats_dir():
        """Assicura che la directory per le chat esista."""
        if not os.path.exists(CHATS_DIR):
            os.makedirs(CHATS_DIR)
            logger.info(f"Creata directory per le chat: {CHATS_DIR}")

    def log_message(self, user_id: int, user_message: str, bot_response: str, 
                   username: Optional[str] = None, first_name: Optional[str] = None) -> bool:
        """
        Registra un messaggio dell'utente e la risposta del bot.
        
        Args:
            user_id: ID dell'utente Telegram
            user_message: Messaggio inviato dall'utente
            bot_response: Risposta inviata dal bot
            username: Nome utente Telegram (opzionale)
            first_name: Nome dell'utente (opzionale)
            
        Returns:
            bool: True se il messaggio è stato registrato correttamente, False altrimenti
        """
        try:
            # Nome del file basato sull'ID utente
            chat_file = os.path.join(CHATS_DIR, f"chat_{user_id}.json")
            
            # Timestamp corrente
            timestamp = datetime.datetime.now().isoformat()
            
            # Dati del messaggio
            message_data = {
                "timestamp": timestamp,
                "user_id": user_id,
                "username": username,
                "first_name": first_name,
                "user_message": user_message,
                "bot_response": bot_response
            }
            
            # Carica i messaggi esistenti o crea un nuovo array
            if os.path.exists(chat_file):
                with open(chat_file, 'r', encoding='utf-8') as f:
                    try:
                        messages = json.load(f)
                    except json.JSONDecodeError:
                        logger.error(f"Errore nel decodificare il file chat {chat_file}, creazione nuovo file")
                        messages = []
            else:
                messages = []
            
            # Aggiungi il nuovo messaggio
            messages.append(message_data)
            
            # Salva il file aggiornato
            with open(chat_file, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Errore durante la registrazione del messaggio: {e}")
            return False

    def get_user_chats(self, user_id: Optional[int] = None) -> Dict[int, List[Dict]]:
        """
        Ottiene le conversazioni degli utenti.
        
        Args:
            user_id: Se specificato, ottiene solo le conversazioni di un utente specifico
            
        Returns:
            Dict: Dizionario con le conversazioni degli utenti
        """
        chats = {}
        
        try:
            if user_id:
                # Leggi solo la chat di un utente specifico
                chat_file = os.path.join(CHATS_DIR, f"chat_{user_id}.json")
                if os.path.exists(chat_file):
                    with open(chat_file, 'r', encoding='utf-8') as f:
                        chats[user_id] = json.load(f)
            else:
                # Leggi tutte le chat
                for filename in os.listdir(CHATS_DIR):
                    if filename.startswith("chat_") and filename.endswith(".json"):
                        try:
                            # Estrai l'ID utente dal nome del file
                            user_id = int(filename.replace("chat_", "").replace(".json", ""))
                            
                            # Leggi il file
                            with open(os.path.join(CHATS_DIR, filename), 'r', encoding='utf-8') as f:
                                chats[user_id] = json.load(f)
                        except (ValueError, json.JSONDecodeError) as e:
                            logger.error(f"Errore nel leggere il file {filename}: {e}")
        except Exception as e:
            logger.error(f"Errore durante il recupero delle chat: {e}")
        
        return chats

    def get_user_info(self) -> List[Dict]:
        """
        Ottiene informazioni su tutti gli utenti che hanno interagito con il bot.
        
        Returns:
            List: Lista di dizionari con le informazioni degli utenti
        """
        users = []
        
        try:
            # Leggi tutte le chat per estrarre le informazioni degli utenti
            chats = self.get_user_chats()
            
            for user_id, messages in chats.items():
                if messages:
                    # Prendi le informazioni dal messaggio più recente
                    latest_message = messages[-1]
                    
                    # Crea il dizionario con le informazioni dell'utente
                    user_info = {
                        "user_id": user_id,
                        "username": latest_message.get("username", ""),
                        "first_name": latest_message.get("first_name", ""),
                        "last_message_time": latest_message.get("timestamp", ""),
                        "message_count": len(messages)
                    }
                    
                    users.append(user_info)
        except Exception as e:
            logger.error(f"Errore durante il recupero delle informazioni degli utenti: {e}")
        
        # Ordina gli utenti per data dell'ultimo messaggio (dal più recente)
        users.sort(key=lambda x: x.get("last_message_time", ""), reverse=True)
        
        return users


# Singleton per il logger delle chat
chat_logger = ChatLogger()