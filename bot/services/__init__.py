# bot/services/__init__.py
"""
Сервисы для работы с внешними API:
- ИИ (GigaChat, YandexGPT)
- Погода
- Рецепты

Автор: MADAO81
"""

from bot.services import ai_service, weather_service, recipe_service

__all__ = [
    'ai_service',
    'weather_service',
    'recipe_service',
]