# bot/core/triggers.py
"""
Система триггеров и реакций бота Пинки Пай.
Реагирует на ключевые слова в сообщениях пользователей.

Автор: MADAO81
"""

import random
import re
from bot.core.constants import TRIGGER_WORDS, TRIGGER_REACTIONS
from bot.core.mood_system import PinkieMood, get_pinkie_phrase


def check_triggers(text: str) -> bool:
    """
    Проверяет, есть ли в тексте триггерные слова.
    """
    text_lower = text.lower()
    for word in TRIGGER_WORDS:
        if word in text_lower:
            return True
    return False


def get_trigger_reaction(text: str, mood: PinkieMood) -> str:
    """
    Возвращает реакцию на триггерное слово.
    """
    text_lower = text.lower()
    
    # Проверяем все триггеры
    for trigger, reactions in TRIGGER_REACTIONS.items():
        if trigger in text_lower:
            # Выбираем случайную реакцию
            reaction = random.choice(reactions)
            
            # Добавляем фирменную фразу в зависимости от настроения
            phrase = get_pinkie_phrase(mood)
            
            # Если Пинки грустная — добавляем грустную нотку
            if mood == PinkieMood.PINKAMENA:
                return f"{reaction}\n\n*тихо добавляет:* {phrase}"
            
            return f"{reaction}\n\n{phrase}"
    
    # Если триггер не найден — возвращаем None
    return None


def get_random_reaction(mood: PinkieMood) -> str:
    """
    Возвращает случайную реакцию на случайное сообщение.
    """
    # Собираем все реакции
    all_reactions = []
    for reactions in TRIGGER_REACTIONS.values():
        all_reactions.extend(reactions)
    
    if not all_reactions:
        return get_pinkie_phrase(mood)
    
    reaction = random.choice(all_reactions)
    phrase = get_pinkie_phrase(mood)
    
    return f"{reaction}\n\n{phrase}"


def extract_trigger_words(text: str) -> list:
    """
    Извлекает все триггерные слова из текста.
    """
    text_lower = text.lower()
    found_triggers = []
    
    for word in TRIGGER_WORDS:
        if word in text_lower:
            found_triggers.append(word)
    
    return found_triggers


def build_trigger_response(triggers: list, mood: PinkieMood) -> str:
    """
    Строит ответ на основе найденных триггеров.
    """
    if not triggers:
        return None
    
    # Если найдено несколько триггеров — выбираем первый
    trigger = triggers[0]
    
    # Ищем реакцию на этот триггер
    for key, reactions in TRIGGER_REACTIONS.items():
        if key in trigger or trigger in key:
            reaction = random.choice(reactions)
            phrase = get_pinkie_phrase(mood)
            
            if mood == PinkieMood.PINKAMENA:
                return f"{reaction}\n\n*тихо:* {phrase}"
            
            return f"{reaction}\n\n{phrase}"
    
    return None


# Добавляем динамические триггеры на основе контекста
class DynamicTriggers:
    """
    Динамические триггеры, которые реагируют на контекст.
    """
    
    @staticmethod
    def check_weather_reaction(is_raining: bool) -> str:
        """
        Реакция на погоду.
        """
        if is_raining:
            return "🌧️ Дождик... Но это не повод грустить! Давайте печь кексы!"
        return "☀️ Какая прекрасная погода! Самое время для вечеринки!"
    
    @staticmethod
    def check_time_reaction(hour: int) -> str:
        """
        Реакция на время суток.
        """
        if 9 <= hour < 12:
            return "☀️ Доброе утро! Время печь свежие кексы!"
        elif 12 <= hour < 17:
            return "🌤️ Отличный день для веселья! Кто со мной?"
        elif 17 <= hour < 20:
            return "🌅 Закат... Самое время для уютной вечеринки!"
        else:
            return "🌙 Скоро я пойду печь кексы... Но пока я с вами!"
