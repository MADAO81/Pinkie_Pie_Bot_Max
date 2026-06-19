# bot/core/__init__.py
"""
Основная логика бота:
- Управление статистикой
- Система настроений
- Триггеры и реакции
- Константы

Автор: MADAO81
"""

from bot.core.constants import *
from bot.core.stats_manager import *
from bot.core.mood_system import *
from bot.core.triggers import *

__all__ = [
    # Константы
    'WEEKLY_JOKE_LIMIT',
    'RESPONSE_COOLDOWN',
    'COOLDOWN_MINUTES',
    'CHANCE_TO_PINKAMENA',
    'CHANCE_TO_COMMENT',
    'CHANCE_TO_SING',
    'WORK_HOURS_START',
    'WORK_HOURS_END',
    'TRIGGER_WORDS',
    'PINKIE_SONGS',
    'PINKIE_PHRASES',
    'TRIGGER_REACTIONS',
    
    # Статистика
    'load_stats',
    'save_stats',
    'can_joke',
    'register_joke',
    'register_user',
    'get_user_stats',
    'reset_weekly_stats',
    
    # Настроения
    'PinkieMood',
    'get_pinkie_mood',
    'get_mood_description',
    'get_mood_advice',
    'get_pinkie_phrase',
    'get_random_song',
    'should_be_silly',
    'get_mood_emoji',
    
    # Триггеры
    'check_triggers',
    'get_trigger_reaction',
    'get_random_reaction',
    'extract_trigger_words',
    'build_trigger_response',
    'DynamicTriggers',
]
