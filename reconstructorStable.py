#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reconstructor de Cookies - v3.2 "Con ZIP Final"
- Pregunta la cantidad exacta de partes para cada paquete.
- Si hay un archivo completo pero está corrupto, lo ignora y usa las partes.
- Verifica que TODAS las partes estén presentes antes de unir.
- Descomprime en carpeta temporal y mueve al destino.
- COPIA el ZIP final (unido o completo) a la carpeta de destino junto con la carpeta descomprimida.
"""

import os
import sys
import zipfile
import shutil
import tempfile
import re
from datetime import datetime
from pathlib import Path

# ============================================================
#                  CONFIGURACIÓN
# ============================================================
CARPETA_ORIGEN = os.path.expanduser("~/Descargas/CookiesZIP")
CARPETA_DESTINO = os.path.expanduser("~/Descargas/CookiesCompletos")
EXTENSION = ".zip"

# ============================================================
#               FUNCIONES AUXILIARES
# ============================================================
def obtener_numero_parte(nombre_archivo):
    """Extrae el número de parte de un nombre de archivo (ej: _part12 -> 12)."""
    match = re.search(r'_part(\d+)\.zip$', nombre_archivo)
    if match:
        return int(match.group(1))
    return None

def obtener_nombre_base(nombre_archivo):
    """Elimina _partN y extensión para obtener el nombre base."""
    if '_part' in nombre_archivo:
        return nombre_archivo.rsplit('_part', 1)[0]
    if nombre_archivo.endswith(EXTENSION):
        return nombre_archivo[:-len(EXTENSION)]
    return nombre_archivo

def es_zip_valido(zip_path):
    """Verifica si un archivo es un ZIP válido."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            return zf.testzip() is None
    except:
        return False

def descomprimir_zip(zip_path, destino):
    """Descomprime un ZIP en la carpeta destino."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(destino)
        return True
    except Exception as e:
        print(f"    [!] Error al descomprimir {os.path.basename(zip_path)}: {e}")
        return False

def unir_partes(partes, nombre_base):
    """Une varias partes de un ZIP en un solo archivo."""
    destino = os.path.join(os.path.dirname(partes[0]), f"{nombre_base}.zip")
    
    with open(destino, 'wb') as outfile:
        for part in partes:
            with open(part, 'rb') as infile:
                outfile.write(infile.read())
    return destino

# ============================================================
#               FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("=" * 60)
    print("  RECONSTRUCTOR DE COOKIES - v3.2 'CON ZIP FINAL'")
    print("=" * 60)

    # 1. Verificar carpeta de origen
    if not os.path.exists(CARPETA_ORIGEN):
        print(f"[!] La carpeta de origen no existe: {CARPETA_ORIGEN}")
        print(f"PROCURA CREARLA MANUALMENTE EN LA RUTA {CARPETA_ORIGEN}")
        sys.exit(1)

    # 2. Crear carpeta de destino si no existe
    os.makedirs(CARPETA_DESTINO, exist_ok=True)
    print(f"[+] Carpeta de destino: {CARPETA_DESTINO}")

    # 3. Buscar todos los archivos ZIP
    archivos_zip = [f for f in os.listdir(CARPETA_ORIGEN) if f.endswith(EXTENSION)]
    if not archivos_zip:
        print(f"[!] No se encontraron archivos {EXTENSION} en {CARPETA_ORIGEN}")
        sys.exit(1)

    print(f"[+] Se encontraron {len(archivos_zip)} archivos ZIP.")

    # 4. Agrupar por paquete base
    paquetes = {}
    for archivo in archivos_zip:
        base = obtener_nombre_base(archivo)
        if base not in paquetes:
            paquetes[base] = []
        paquetes[base].append(archivo)

    print(f"[+] Se detectaron {len(paquetes)} paquetes.")
    
    # 5. Mostrar información de cada paquete
    print("\n" + "=" * 60)
    print("  INFORMACIÓN DE PAQUETES DETECTADOS")
    print("=" * 60)
    
    paquetes_info = {}
    for base, archivos in sorted(paquetes.items()):
        partes = []
        completos = []
        for archivo in archivos:
            num = obtener_numero_parte(archivo)
            if num is not None:
                partes.append(num)
            else:
                completos.append(archivo)
        
        partes.sort()
        
        print(f"\n📦 Paquete: {base}")
        print(f"   - Archivos totales: {len(archivos)}")
        if completos:
            print(f"   - Archivos completos: {', '.join(completos)}")
        if partes:
            print(f"   - Partes detectadas: {len(partes)}")
            print(f"   - Números de parte: {partes[:10]}{'...' if len(partes) > 10 else ''}")
        
        paquetes_info[base] = {
            'archivos': archivos,
            'partes': partes,
            'completos': completos,
            'total_parts': len(partes),
            'max_parts': max(partes) if partes else 0
        }
    
    # 6. Preguntar la cantidad exacta de partes
    print("\n" + "=" * 60)
    print("  VERIFICACIÓN DE PARTES (RESPONDER CON NÚMERO EXACTO)")
    print("=" * 60)
    
    for base, info in paquetes_info.items():
        if info['partes'] or info['completos']:
            while True:
                respuesta = input(f"\n¿Cuántas partes tiene el paquete '{base}'? (Número exacto): ")
                if respuesta.strip().isdigit():
                    partes_esperadas = int(respuesta)
                    break
                else:
                    print("   ❌ Debes ingresar un número entero.")
            
            print(f"   ✅ Esperando {partes_esperadas} partes.")
            
            esperadas = set(range(1, partes_esperadas + 1))
            presentes = set(info['partes'])
            faltantes = esperadas - presentes
            sobrantes = presentes - esperadas
            
            if faltantes:
                print(f"   ❌ ERROR: Faltan las partes: {sorted(faltantes)}")
                print(f"   ❌ No se puede reconstruir el paquete '{base}'.")
                print("   Deteniendo el proceso.")
                sys.exit(1)
            if sobrantes:
                print(f"   ⚠️  Sobran partes (posible error en el nombre): {sorted(sobrantes)}")
                print("   Continuando con las partes esperadas...")
    
    # 7. Crear carpeta temporal
    temp_dir = tempfile.mkdtemp(prefix="reconstructor_")
    print(f"\n[+] Carpeta temporal: {temp_dir}")
    
    # 8. Procesar cada paquete
    total_procesados = 0
    for base, info in paquetes_info.items():
        print(f"\n[*] Procesando paquete: {base}")
        
        zip_final = None  # Aquí guardaremos la ruta del ZIP final (unido o completo)
        zip_unido = None
        
        # Verificar si el archivo completo existe y es válido
        if info['completos']:
            archivo_completo = info['completos'][0]
            ruta_completa = os.path.join(CARPETA_ORIGEN, archivo_completo)
            
            if es_zip_valido(ruta_completa):
                print(f"    ✅ Usando archivo completo: {archivo_completo}")
                zip_unido = ruta_completa
                zip_final = ruta_completa  # El ZIP final es el completo
            else:
                print(f"    ⚠️  El archivo completo '{archivo_completo}' está CORRUPTO o no es un ZIP válido.")
                print(f"    Intentando reconstruir desde partes...")
                info['completos'] = []
        
        # Si no hay ZIP válido, usar partes
        if zip_unido is None and info['partes']:
            partes_ordenadas = sorted(info['partes'])
            rutas_partes = [os.path.join(CARPETA_ORIGEN, f"{base}_part{p}.zip") for p in partes_ordenadas]
            
            for ruta in rutas_partes:
                if not os.path.exists(ruta):
                    print(f"    ❌ Error: La parte {os.path.basename(ruta)} no existe en disco.")
                    print("   Deteniendo el proceso.")
                    sys.exit(1)
            
            print(f"    -> Uniendo {len(rutas_partes)} partes...")
            zip_unido = unir_partes(rutas_partes, base)
            zip_final = zip_unido  # El ZIP final es el que acabamos de unir
            print(f"    -> ZIP unido: {os.path.basename(zip_unido)}")
        
        if zip_unido is None:
            print(f"    ❌ No hay archivos válidos para este paquete. Deteniendo.")
            sys.exit(1)
        
        if not es_zip_valido(zip_unido):
            print(f"    ❌ El ZIP unido NO es válido. Deteniendo.")
            if '_part' in base and os.path.exists(zip_unido):
                os.remove(zip_unido)
            sys.exit(1)
        
        # Descomprimir en carpeta temporal
        print(f"    -> Descomprimiendo en carpeta temporal...")
        if descomprimir_zip(zip_unido, temp_dir):
            print(f"    ✅ Descompresión exitosa.")
            total_procesados += 1
        else:
            print(f"    ❌ Falló la descompresión. Deteniendo.")
            sys.exit(1)
        
        # COPIAR EL ZIP FINAL A LA CARPETA DE DESTINO (junto con la carpeta descomprimida)
        if zip_final and os.path.exists(zip_final):
            destino_zip = os.path.join(CARPETA_DESTINO, os.path.basename(zip_final))
            # Si ya existe, añadir sufijo
            contador = 1
            while os.path.exists(destino_zip):
                nombre_base_zip, ext = os.path.splitext(os.path.basename(zip_final))
                destino_zip = os.path.join(CARPETA_DESTINO, f"{nombre_base_zip}_{contador}{ext}")
                contador += 1
            shutil.copy2(zip_final, destino_zip)
            print(f"    ✅ ZIP final copiado a: {destino_zip}")
        
        # Limpiar ZIP unido temporal (si se creó)
        if '_part' in base and os.path.exists(zip_unido):
            os.remove(zip_unido)
    
    # 9. Mover carpeta temporal al destino
    fecha = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    nombre_destino = f"Cookies_Unificadas_{fecha}"
    destino_final = os.path.join(CARPETA_DESTINO, nombre_destino)
    
    contador = 1
    while os.path.exists(destino_final):
        destino_final = os.path.join(CARPETA_DESTINO, f"{nombre_destino}_{contador}")
        contador += 1
    
    shutil.move(temp_dir, destino_final)
    print(f"\n[+] Carpeta unificada movida a: {destino_final}")
    
    # 10. Resumen final
    print("\n" + "=" * 60)
    print("  RECONSTRUCCIÓN COMPLETADA CON ÉXITO.")
    print(f"  Paquetes procesados: {len(paquetes)}")
    print(f"  Archivos ZIP procesados: {len(archivos_zip)}")
    print(f"  Ubicación de la carpeta: {destino_final}")
    print(f"  ZIP final guardado en: {CARPETA_DESTINO}")
    print("=" * 60)

if __name__ == "__main__":
    main()