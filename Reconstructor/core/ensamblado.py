#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/ensamblado.py
- Une varias partes de un ZIP en un solo archivo.
"""

import os


def unir_partes(partes, nombre_base):
    """Une varias partes de un ZIP en un solo archivo."""
    destino = os.path.join(os.path.dirname(partes[0]), f"{nombre_base}.zip")

    with open(destino, 'wb') as outfile:
        for part in partes:
            with open(part, 'rb') as infile:
                outfile.write(infile.read())
    return destino