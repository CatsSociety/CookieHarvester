#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
core/perfiles.py
- Busca las carpetas de perfiles de Firefox, Chrome y Brave.
- Retorna la ruta del perfil o None si no se encuentra.
"""

import os


def encontrar_perfil_firefox():
    """
    Busca el perfil de Firefox con cookies.sqlite.
    Recorre varias rutas posibles según distro/instalación.
    """
    base = os.path.expanduser('~')
    rutas_posibles = [
        os.path.join(base, '.mozilla', 'firefox'),  # Ruta por defecto en Linux mayormente.
        os.path.join(base, '.config', 'mozilla', 'firefox'),
        os.path.join(base, '.config', '.mozilla', 'firefox'),
        os.path.join(base, '.var', 'app', 'org.mozilla.firefox', '.mozilla', 'firefox'),
        os.path.join(base, 'snap', 'firefox', 'common', '.mozilla', 'firefox'),
    ]
    for ruta_base in rutas_posibles:
        if not os.path.exists(ruta_base):
            continue
        for perfil in os.listdir(ruta_base):
            if perfil.endswith('.default-release') or perfil.endswith('.default'):
                ruta_perfil = os.path.join(ruta_base, perfil)
                if os.path.exists(os.path.join(ruta_perfil, 'cookies.sqlite')):
                    return ruta_perfil
    return None


def encontrar_perfil_chrome():
    """
    Busca el perfil de Chrome (solo si SOPORTE_CHROME es True).
    Es experimental.
    """
    # Importamos aquí para evitar dependencia circular con config.
    from config import SOPORTE_CHROME
    if not SOPORTE_CHROME:
        return None
    base = os.path.expanduser('~')
    rutas = [
        os.path.join(base, '.config', 'google-chrome', 'Default'),
        os.path.join(base, '.var', 'app', 'com.google.Chrome', 'config', 'google-chrome', 'Default'),
    ]
    for ruta in rutas:
        if os.path.exists(os.path.join(ruta, 'Network', 'Cookies')):
            return ruta
    return None


def encontrar_perfil_brave():
    """
    Busca el perfil de Brave (solo si SOPORTE_CHROME es True).
    Es experimental.
    """
    from config import SOPORTE_CHROME
    if not SOPORTE_CHROME:
        return None
    base = os.path.expanduser('~')
    ruta = os.path.join(base, '.config', 'BraveSoftware', 'Brave-Browser', 'Default')
    if os.path.exists(os.path.join(ruta, 'Network', 'Cookies')):
        return ruta
    return None