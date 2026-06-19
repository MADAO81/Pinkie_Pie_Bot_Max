# bot/services/__init__.py
"""
Сервисы для работы с внешними API:
- ИИ (GigaChat, YandexGPT)
- Погода (OpenWeatherMap)
- Рецепты (andychef.ru)

Автор: MADAO81
"""

from bot.services.weather_service import *
from bot.services.recipe_service import *

__all__ = [
    # Погода
    'get_weather',
    'get_forecast',
    'is_bad_weather',
    'get_weather_emoji',
    'format_weather_message',
    'get_weather_mood_influence',
    
    # Рецепты
    'get_random_recipe',
    'get_recipe_list',
    'parse_recipe_page',
    'get_daily_recipe',
    'format_recipe_for_chat',
]
