#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/nombres.py
- Utilidades para parsear nombres de archivos ZIP.
- Extrae número de parte y nombre base.
"""

import re
from config import EXTENSION


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