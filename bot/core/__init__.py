# bot/core/__init__.py
"""
Основная логика бота:
- Управление статистикой
- Система настроений
- Триггеры и реакции
- Константы

Автор: MADAO81
"""

from bot.core import stats_manager, mood_system, triggers, constants

__all__ = [
    'stats_manager',
    'mood_system',
    'triggers',
    'constants',
]