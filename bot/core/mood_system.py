# bot/core/mood_system.py
"""
Система настроений Пинки Пай.
Управляет настроением бота в зависимости от погоды и случайных факторов.

Автор: MADAO81
"""

import random
from enum import Enum
from bot.services.weather_service import is_bad_weather
from bot.core.constants import CHANCE_TO_PINKAMENA, PINKIE_PHRASES


class PinkieMood(Enum):
    """Перечисление возможных настроений Пинки Пай"""
    HAPPY = "happy"          # Весёлое
    PINKAMENA = "pinkamena"  # Грустное (Пинкамина Диана Пай)
    SILLY = "silly"          # Дурашливое (редко, для разнообразия)


# Кэш для хранения текущего настроения
_mood_cache = {
    'mood': PinkieMood.HAPPY,
    'description': 'Весёлая и энергичная пони! 🎉',
    'last_update': None
}


def get_pinkie_mood(force_refresh: bool = False):
    """
    Возвращает текущее настроение Пинки Пай.
    Учитывает погоду и случайные факторы.
    """
    global _mood_cache
    
    # Если не нужно обновлять и есть кэш — возвращаем его
    if not force_refresh and _mood_cache.get('last_update'):
        return _mood_cache['mood'], _mood_cache['description']
    
    # Проверяем погоду
    weather_bad = is_bad_weather()
    
    # Определяем настроение
    if weather_bad and random.random() < CHANCE_TO_PINKAMENA:
        mood = PinkieMood.PINKAMENA
        description = "Немного грустная Пинкамина Диана Пай... 🌧️"
    elif random.random() < 0.10:  # 10% шанс на дурашливое настроение
        mood = PinkieMood.SILLY
        description = "Супер-странная и дурашливая! 🤪"
    else:
        mood = PinkieMood.HAPPY
        description = "Весёлая и энергичная пони! 🎉"
    
    # Обновляем кэш
    _mood_cache['mood'] = mood
    _mood_cache['description'] = description
    _mood_cache['last_update'] = True
    
    return mood, description


def get_mood_description(mood: PinkieMood) -> str:
    """
    Возвращает описание настроения.
    """
    descriptions = {
        PinkieMood.HAPPY: "🎈 Я полна энергии и готова веселиться!",
        PinkieMood.PINKAMENA: "🌧️ Сегодня немного пасмурно, но я всё равно с вами!",
        PinkieMood.SILLY: "🤪 У меня сегодня супер-странное настроение!"
    }
    return descriptions.get(mood, "🤔 Настроение загадочное...")


def get_mood_advice(mood: PinkieMood) -> str:
    """
    Возвращает совет для чата в зависимости от настроения.
    """
    advices = {
        PinkieMood.HAPPY: "Давайте устроим вечеринку! 🎉 Кто со мной?",
        PinkieMood.PINKAMENA: "Мне нужно немного уюта и тепла. Или кексов! 🧁",
        PinkieMood.SILLY: "Я готова наделать глупостей! Кто со мной в авантюру? 🦄"
    }
    return advices.get(mood, "Просто будьте собой и улыбайтесь!")


def get_pinkie_phrase(mood: PinkieMood) -> str:
    """
    Возвращает случайную фирменную фразу Пинки Пай.
    """
    mood_key = mood.value if hasattr(mood, 'value') else str(mood)
    phrases = PINKIE_PHRASES.get(mood_key, PINKIE_PHRASES['happy'])
    return random.choice(phrases)


def get_random_song() -> str:
    """
    Возвращает случайную песенку Пинки Пай.
    """
    from bot.core.constants import PINKIE_SONGS
    return random.choice(PINKIE_SONGS)


def should_be_silly(mood: PinkieMood) -> bool:
    """
    Проверяет, должна ли Пинки быть дурашливой.
    """
    return mood == PinkieMood.SILLY or (mood == PinkieMood.HAPPY and random.random() < 0.10)


def get_mood_emoji(mood: PinkieMood) -> str:
    """
    Возвращает эмодзи для настроения.
    """
    emojis = {
        PinkieMood.HAPPY: "🦄✨",
        PinkieMood.PINKAMENA: "🌧️💭",
        PinkieMood.SILLY: "🤪🎈"
    }
    return emojis.get(mood, "🦄")
