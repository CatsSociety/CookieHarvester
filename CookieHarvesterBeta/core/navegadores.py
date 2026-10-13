#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/navegadores.py
- Detecta qué navegadores están abiertos en el sistema.
- Usa pgrep para verificar procesos activos.
"""

import subprocess


def navegador_abierto(nombre_proceso):
    """
    Verifica si un proceso (navegador) está en ejecución usando pgrep.
    Retorna True si está abierto, False si no.
    """
    try:
        resultado = subprocess.run(
            ['pgrep', '-x', nombre_proceso],
            capture_output=True,
            text=True
        )
        return resultado.returncode == 0
    except:
        return False


def detectar_navegadores_abiertos():
    """
    Recorre una lista de navegadores y verifica cuáles están abiertos.
    Solo retorna lista de nombres legibles.
    """
    procesos = {
        'firefox': 'Firefox',
        'chrome': 'Chrome',
        'chromium': 'Chromium',
        'brave': 'Brave',
        'microsoft-edge': 'Edge',
    }
    abiertos = []
    for proc, nombre in procesos.items():
        if navegador_abierto(proc):
            abiertos.append(nombre)
    return abiertos