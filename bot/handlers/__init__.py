# bot/handlers/__init__.py
"""
Обработчики команд и сообщений для бота Пинки Пай.

Автор: MADAO81
"""

from bot.handlers.commands import router as commands_router
from bot.handlers.messages import router as messages_router

__all__ = [
    'commands_router',
    'messages_router',
]
