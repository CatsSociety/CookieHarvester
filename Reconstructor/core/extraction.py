#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/extraction.py
- Descomprime un ZIP en una carpeta destino.
"""

import os
import zipfile


def descomprimir_zip(zip_path, destino):
    """Descomprime un ZIP en la carpeta destino."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(destino)
        return True
    except Exception as e:
        print(f"[!!] Error al descomprimir {os.path.basename(zip_path)}: {e}")
        return False