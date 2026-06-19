# bot/__init__.py
"""
Пакет бота Пинки Пай для мессенджера MAX.
Содержит всю логику работы бота, обработчики, сервисы и утилиты.

Автор: MADAO81
"""

from bot.config import Config
from bot.main import main

__all__ = [
    'Config',
    'main',
]

__version__ = '1.0.0'
__author__ = 'MADAO81'