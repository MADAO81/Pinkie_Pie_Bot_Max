# bot/utils/__init__.py
"""
Вспомогательные утилиты:
- Работа со временем
- Обработка текста

Автор: MADAO81
"""

from bot.utils.time_utils import *
from bot.utils.text_utils import *

__all__ = [
    # time_utils
    'is_working_hours',
    'is_weekend',
    'get_working_hours_status',
    'can_respond',
    'update_response_time',
    'get_time_until_next_work',
    'format_timestamp',
    'get_week_day_name',
    'is_time_to_sing',
    'get_time_greeting',
    
    # text_utils
    'clean_text',
    'truncate_text',
    'extract_mentions',
    'extract_keywords',
    'remove_emoji',
    'normalize_text',
    'split_text_by_length',
    'format_bold',
    'format_italic',
    'format_code',
    'format_strikethrough',
    'capitalize_first',
    'is_question',
    'get_random_emoji',
    'add_random_emoji',
    'escape_markdown',
]
