import base64
import os
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, DEFAULT_SYSTEM_MESSAGE, MAX_TOKENS, TEMPERATURE
import logging

logger = logging.getLogger(__name__)

# Initialize the OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

class Conversation:
    """Class to handle conversation history and context for a user"""

    def __init__(self, user_id):
        self.user_id = user_id
        self.messages = [{"role": "system", "content": DEFAULT_SYSTEM_MESSAGE}]

    def add_message(self, role, content):
        """Add a message to the conversation history"""
        self.messages.append({"role": role, "content": content})

        # Keep conversation history at a reasonable size
        if len(self.messages) > 10:  # Keep system message plus last 9 exchanges
            self.messages = [self.messages[0]] + self.messages[-9:]

    def get_messages(self):
        """Get all messages in the conversation"""
        return self.messages


class OpenAIHandler:
    """Class to handle interactions with the OpenAI API"""

    def __init__(self):
        self.conversations = {}  # Dictionary to store conversations by user_id

    def get_conversation(self, user_id):
        """Get or create conversation for a user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = Conversation(user_id)
        return self.conversations[user_id]

    def reset_conversation(self, user_id):
        """Reset a user's conversation history"""
        self.conversations[user_id] = Conversation(user_id)
        return "Conversation history has been reset."

    def analyze_image(self, user_id, base64_image):
        """Analizza un'immagine usando GPT-4o"""
        try:
            logger.info(f"Invio immagine a OpenAI GPT-4o per l'utente {user_id}")
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Descrivi dettagliatamente l'immagine inviata."},
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Errore nell'analisi immagine: {e}")
            return "Non sono riuscito ad analizzare l'immagine. Riprova più tardi."
    
    def generate_response(self, user_id, message_text):
        """Generate a response using OpenAI API"""
        conversation = self.get_conversation(user_id)
        conversation.add_message("user", message_text)
        
        try:
            logger.info(f"Sending request to OpenAI for user {user_id}")
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=conversation.get_messages(),
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )

            assistant_response = response.choices[0].message.content
            conversation.add_message("assistant", assistant_response)

            return assistant_response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            if "insufficient_quota" in str(e):
                return (
                    "Mi dispiace, ma al momento non posso accedere all'intelligenza artificiale "
                    "a causa di un problema con il limite di utilizzo. "
                    "Il proprietario del bot è stato avvisato del problema. "
                    "Riprova più tardi."
                )
            else:
                return (
                    "Mi dispiace, ma sto avendo problemi a connettermi all'intelligenza artificiale. "
                    "Riprova tra qualche momento."
                )
