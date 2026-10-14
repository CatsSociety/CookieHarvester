#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/copy.py
- Copia una carpeta completa a otro destino.
- Muestra errores si falla la copia.
"""

import os
import shutil


def copiar_carpeta(origen, destino):
    """
    Copia una carpeta completa usando shutil.copytree.
    Retorna True si tuvo éxito, False si falló.
    """
    try:
        if os.path.exists(destino):
            shutil.rmtree(destino)
        shutil.copytree(origen, destino, symlinks=False, ignore_dangling_symlinks=True)
        return True
    except Exception as e:
        print(f"    [!] Error copiando: {e}")
        return False