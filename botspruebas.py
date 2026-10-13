from dotenv import load_dotenv
import os
load_dotenv()
TOKEN = os.getenv("TOKEN_TL")
CHAT_ID = os.getenv("CHAT_ID")
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests



session = requests.Session()

session.mount('https://', HTTPAdapter(max_retries=Retry(total=3, backoff_factor=1)))
def enviar_mensaje(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": texto
    }
    try:
        respuesta = session.post(url, data=payload, timeout=10)
        return respuesta.json()
    except requests.exceptions.ConnectionError as e:
        print(f"Error de conexion: {e}")
        return None

if __name__ == "__main__":
    enviar_mensaje("¡Hola! Este es un mensaje enviado por mi bot.")