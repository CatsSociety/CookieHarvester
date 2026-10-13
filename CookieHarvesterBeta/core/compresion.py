#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/compresion.py
- Comprime una carpeta en ZIP.
- Divide el ZIP en partes de MAX_SIZE_MB.
"""

import os
import zipfile
from math import ceil


def crear_zip_desde_carpeta(carpeta_origen, zip_destino):
    """
    Comprime una carpeta en un archivo ZIP.
    Retorna la ruta del ZIP creado.
    """
    with zipfile.ZipFile(zip_destino, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(carpeta_origen):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, carpeta_origen)
                zf.write(full_path, arcname)
    return zip_destino


def dividir_zip_en_partes(zip_path, max_size_mb=8):
    """
    Divide un ZIP en partes de max_size_mb MB.
    Retorna una lista con las rutas de las partes.
    Si el ZIP es más pequeño que el límite, retorna [zip_path].
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