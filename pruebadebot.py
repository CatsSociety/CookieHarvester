import os
import requests
from dotenv import load_dotenv

load_dotenv()

API = os.getenv("API_Discord")

data = {
    "content": "Hola we"
}

response = requests.post(API, json=data)

if response.status_code == 204:
    print("Funciona")
else:
    print(f"Error: {response.status_code}")
