#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Reconstructor de Cookies
- El ZIP final y la carpeta final usan el mismo nombre base que los ZIPs originales.
- Pregunta la cantidad exacta de partes para cada paquete.
- Si hay un archivo completo pero está corrupto, lo ignora y usa las partes.
- Verifica que TODAS las partes estén presentes antes de unir.
- Descomprime directamente en el destino con el nombre base.
- COPIA el ZIP final al destino.
- ELIMINA SOLO los archivos del paquete procesado (ZIP final y partes) de la carpeta de origen.
- Respeta el resto de archivos ZIP que no pertenecen al paquete.
"""

import os
import sys
import shutil

# Configuración global.
from config import (
    VERSION,
    CARPETA_ORIGEN,
    CARPETA_DESTINO,
    EXTENSION,
    ELIMINAR_ORIGEN,
)

# Lógica de negocio.
from core.nombres import obtener_numero_parte, obtener_nombre_base
from core.verificacion import es_zip_valido
from core.ensamblado import unir_partes
from core.extraccion import descomprimir_zip
from core.limpieza import limpiar_origen_selectiva


# ============================================================
#               FUNCIÓN PRINCIPAL
# ============================================================
def main():
    print("=" * 60)
    print(f"  RECONSTRUCTOR DE COOKIES - {VERSION} ")
    print("=" * 60)

    # 1. Verificar carpeta de origen
    if not os.path.exists(CARPETA_ORIGEN):
        print(f"[!] La carpeta de origen no existe: {CARPETA_ORIGEN}")
        print(f"[o] Crea la carpeta con: mkdir -p {CARPETA_ORIGEN}")
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
                    print("[X] Debes ingresar un número entero.")

            print(f"[OK] Esperando {partes_esperadas} partes.")

            esperadas = set(range(1, partes_esperadas + 1))
            presentes = set(info['partes'])
            faltantes = esperadas - presentes
            sobrantes = presentes - esperadas

            if faltantes:
                print(f"[X] ERROR: Faltan las partes: {sorted(faltantes)}")
                print(f"[X] No se puede reconstruir el paquete '{base}'.")
                print("   Deteniendo el proceso.")
                sys.exit(1)
            if sobrantes:
                print(f"[!!] Sobran partes (posible error en el nombre): {sorted(sobrantes)}")
                print("   Continuando con las partes esperadas...")

    # 7. Procesar cada paquete
    total_procesados = 0
    for base, info in paquetes_info.items():
        print(f"\n[*] Procesando paquete: {base}")

        zip_final = None
        zip_unido = None
        archivos_a_eliminar = []  # Lista de nombres de archivos a eliminar (solo este paquete)

        # Verificar si el archivo completo existe y es válido
        if info['completos']:
            archivo_completo = info['completos'][0]
            ruta_completa = os.path.join(CARPETA_ORIGEN, archivo_completo)
            archivos_a_eliminar.append(archivo_completo)

            if es_zip_valido(ruta_completa):
                print(f"[OK] Usando archivo completo: {archivo_completo}")
                zip_unido = ruta_completa
                zip_final = ruta_completa
            else:
                print(f"[!!] El archivo completo '{archivo_completo}' está CORRUPTO o no es un ZIP válido.")
                print(f"    Intentando reconstruir desde partes...")
                info['completos'] = []

        # Si no hay ZIP válido, usar partes
        if zip_unido is None and info['partes']:
            partes_ordenadas = sorted(info['partes'])
            # Generar nombres de archivos para las partes
            for p in partes_ordenadas:
                archivos_a_eliminar.append(f"{base}_part{p}.zip")

            rutas_partes = [os.path.join(CARPETA_ORIGEN, f"{base}_part{p}.zip") for p in partes_ordenadas]

            for ruta in rutas_partes:
                if not os.path.exists(ruta):
                    print(f"[X] Error: La parte {os.path.basename(ruta)} no existe en disco.")
                    print("   Deteniendo el proceso.")
                    sys.exit(1)

            print(f"    -> Uniendo {len(rutas_partes)} partes...")
            zip_unido = unir_partes(rutas_partes, base)
            zip_final = zip_unido
            # Añadir el ZIP unido a la lista de archivos a eliminar
            archivos_a_eliminar.append(os.path.basename(zip_unido))
            print(f"    -> ZIP unido: {os.path.basename(zip_unido)}")

        if zip_unido is None:
            print(f"[X] No hay archivos válidos para este paquete. Deteniendo.")
            sys.exit(1)

        if not es_zip_valido(zip_unido):
            print(f"[X] El ZIP unido NO es válido. Deteniendo.")
            if '_part' in base and os.path.exists(zip_unido):
                os.remove(zip_unido)
            sys.exit(1)

        # Crear carpeta de destino con el mismo nombre base
        destino_paquete = os.path.join(CARPETA_DESTINO, base)
        contador = 1
        while os.path.exists(destino_paquete):
            destino_paquete = os.path.join(CARPETA_DESTINO, f"{base}_{contador}")
            contador += 1

        # Descomprimir directamente en la carpeta destino
        print(f"    -> Descomprimiendo en: {destino_paquete}")
        os.makedirs(destino_paquete, exist_ok=True)
        if descomprimir_zip(zip_unido, destino_paquete):
            print(f"[OK] Descompresión exitosa.")
            total_procesados += 1
        else:
            print(f"[X] Falló la descompresión. Deteniendo.")
            sys.exit(1)

        # COPIAR EL ZIP FINAL con el mismo nombre base
        if zip_final and os.path.exists(zip_final):
            nombre_zip_final = f"{base}.zip"
            destino_zip = os.path.join(CARPETA_DESTINO, nombre_zip_final)
            contador_zip = 1
            while os.path.exists(destino_zip):
                nombre_base_zip, ext = os.path.splitext(nombre_zip_final)
                destino_zip = os.path.join(CARPETA_DESTINO, f"{nombre_base_zip}_{contador_zip}{ext}")
                contador_zip += 1
            shutil.copy2(zip_final, destino_zip)
            print(f"[OK] ZIP final copiado a: {destino_zip}")

        # LIMPIAR SOLO LOS ARCHIVOS DE ESTE PAQUETE (no los de otros)
        limpiar_origen_selectiva(base, archivos_a_eliminar)

        # Limpiar ZIP unido temporal (si se creó)
        if '_part' in base and os.path.exists(zip_unido) and zip_unido not in archivos_a_eliminar:
            try:
                os.remove(zip_unido)
            except:
                pass

    # 8. Resumen final
    print("\n" + "=" * 60)
    print("  RECONSTRUCCIÓN COMPLETADA CON ÉXITO.")
    print(f"  Paquetes procesados: {len(paquetes)}")
    print(f"  Archivos ZIP procesados: {len(archivos_zip)}")
    print(f"  Ubicación de la carpeta: {CARPETA_DESTINO}")
    print(f"  Nombre del paquete final: {base}")
    if ELIMINAR_ORIGEN:
        print("[OK] Archivos de origen eliminados (solo los de los paquetes procesados).")
    print("=" * 60)
    print(f"Corralos con el comando: firefox -profile {CARPETA_DESTINO}/{base} -no-remote")


if __name__ == "__main__":
    main()