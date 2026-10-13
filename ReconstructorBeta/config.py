#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
config.py
- Configuración global del Reconstructor.
- Define rutas de origen/destino y flags de comportamiento.
"""

import os

# ============================================================
#                  CONFIGURACIÓN
# ============================================================

# --- versiones ---
VERSION = "v3.5.1" # Version actual
# VERSION = "v3.5.0" # Version anterior

# Configuraciones
CARPETA_ORIGEN = os.path.expanduser("~/Descargas/CookiesZIP")
CARPETA_DESTINO = os.path.expanduser("~/Descargas/CookiesCompletos")
EXTENSION = ".zip"
ELIMINAR_ORIGEN = True  # Si es True, elimina solo los archivos del paquete procesado