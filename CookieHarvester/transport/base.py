#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
transport/base.py
- Interfaz abstracta para los transportes.
- Define el contrato que todo transporte debe cumplir.
"""

from abc import ABC, abstractmethod


class Transport(ABC):
    """
    Contrato mínimo de un transporte.
    Cualquier transporte (Discord, Telegram, etc.) debe implementar estos métodos.
    """

    @abstractmethod
    def send_text(self, texto: str) -> bool:
        """Envía un mensaje de texto. Retorna True/False."""
        pass

    @abstractmethod
    def send_file(self, filepath: str, caption: str = None,
                  intento: int = 1, max_intentos: int = 3) -> bool:
        """Envía un archivo. Retorna True/False."""
        pass

    @abstractmethod
    def send_summary(self, resumen: str) -> bool:
        """Envía el resumen final. Retorna True/False."""
        pass