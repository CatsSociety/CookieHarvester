import os
import requests
from dotenv import load_dotenv

load_dotenv()

# PRUEBA TU BOT DE DISCORD AQUI
# NO OLVIDES PONER TUS CREDENCIALES EN .env

API = os.getenv("API_Discord")

data = {
    # Edita el mensaje
    "content": "Hola we, soy tu bot de Discord"
}

response = requests.post(API, json=data)

if response.status_code == 204:
    print("Funciona")
else:
    print(f"Error: {response.status_code}")
