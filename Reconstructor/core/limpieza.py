#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/limpieza.py
- Elimina SOLO los archivos del paquete procesado de la carpeta de origen.
- Respeta el resto de archivos que no pertenecen al paquete.
"""

import os
from config import CARPETA_ORIGEN, ELIMINAR_ORIGEN


def limpiar_origen_selectiva(paquete_base, archivos_a_eliminar):
    """
    Elimina SOLO los archivos del paquete procesado.
    archivos_a_eliminar: lista de nombres de archivos (partes y ZIP final)
                         que pertenecen a este paquete.
    """
    if not ELIMINAR_ORIGEN:
        return

    print(f"    -> Limpiando archivos de origen (solo los de este paquete)...")
    eliminados = 0
    for archivo in archivos_a_eliminar:
        ruta = os.path.join(CARPETA_ORIGEN, archivo)
        if os.path.exists(ruta):
            try:
                os.remove(ruta)
                eliminados += 1
                print(f"       Eliminado: {archivo}")
            except Exception as e:
                print(f"[!!] Error al eliminar {archivo}: {e}")

    if eliminados > 0:
        print(f"[OK] Eliminados {eliminados} archivos del paquete '{paquete_base}' de la carpeta de origen.")
    else:
        print(f"[!!] No se encontraron archivos del paquete '{paquete_base}' para eliminar.")