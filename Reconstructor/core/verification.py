#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/verification.py
- Verifica si un archivo es un ZIP válido.
"""

import zipfile


def es_zip_valido(zip_path):
    """Verifica si un archivo es un ZIP válido."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            return zf.testzip() is None
    except:
        return False