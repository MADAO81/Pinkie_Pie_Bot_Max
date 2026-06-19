# bot/utils/text_utils.py
"""
Утилиты для работы с текстом.
Очистка, форматирование, обработка строк.

Автор: MADAO81
"""

import re
import unicodedata
from typing import List, Optional


def clean_text(text: str) -> str:
    """
    Очищает текст от лишних пробелов и спецсимволов.
    """
    if not text:
        return ""
    
    # Убираем лишние пробелы
    text = re.sub(r'\s+', ' ', text)
    
    # Убираем эмодзи (опционально)
    # text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
    
    return text.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Обрезает текст до указанной длины с добавлением многоточия.
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - 3] + "..."


def extract_mentions(text: str) -> List[str]:
    """
    Извлекает все упоминания (@username) из текста.
    """
    if not text:
        return []
    
    pattern = r'@\w+'
    return re.findall(pattern, text)


def extract_keywords(text: str, keywords: List[str]) -> List[str]:
    """
    Находит в тексте слова из заданного списка.
    """
    if not text or not keywords:
        return []
    
    text_lower = text.lower()
    found = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            found.append(keyword)
    
    return found


def remove_emoji(text: str) -> str:
    """
    Удаляет эмодзи из текста.
    """
    if not text:
        return ""
    
    emoji_pattern = re.compile(
        "[\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"   # symbols & pictographs
        "\U0001F680-\U0001F6FF"   # transport & map symbols
        "\U0001F700-\U0001F77F"   # alchemical symbols
        "\U0001F780-\U0001F7FF"   # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"   # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"   # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"   # Chess Symbols
        "\U0001FA70-\U0001FAFF"   # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"   # Dingbats
        "\U000024C2-\U0001F251"   # Enclosed characters
        "]+",
        flags=re.UNICODE
    )
    
    return emoji_pattern.sub('', text)


def normalize_text(text: str) -> str:
    """
    Нормализует текст: убирает диакритические знаки, приводит к нижнему регистру.
    """
    if not text:
        return ""
    
    # Приводим к нижнему регистру
    text = text.lower()
    
    # Нормализуем Unicode
    text = unicodedata.normalize('NFKD', text)
    
    # Убираем диакритические знаки
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    
    return text.strip()


def split_text_by_length(text: str, max_length: int = 4096) -> List[str]:
    """
    Разбивает длинный текст на части по указанной длине.
    Полезно для отправки длинных сообщений.
    """
    if not text:
        return []
    
    if len(text) <= max_length:
        return [text]
    
    parts = []
    current_part = ""
    
    for sentence in text.split('. '):
        if len(current_part) + len(sentence) + 2 <= max_length:
            current_part += sentence + ". "
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = sentence + ". "
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts


def format_bold(text: str) -> str:
    """Форматирует текст жирным (Markdown)."""
    return f"*{text}*"


def format_italic(text: str) -> str:
    """Форматирует текст курсивом (Markdown)."""
    return f"_{text}_"


def format_code(text: str) -> str:
    """Форматирует текст как код (Markdown)."""
    return f"`{text}`"


def format_strikethrough(text: str) -> str:
    """Форматирует текст как зачёркнутый (Markdown)."""
    return f"~{text}~"


def capitalize_first(text: str) -> str:
    """
    Делает первую букву заглавной, остальные в нижнем регистре.
    """
    if not text:
        return ""
    
    return text[0].upper() + text[1:].lower()


def is_question(text: str) -> bool:
    """
    Проверяет, является ли текст вопросом.
    """
    if not text:
        return False
    
    text = text.strip()
    
    # Проверяем наличие вопросительного знака
    if text.endswith('?'):
        return True
    
    # Проверяем вопросительные слова
    question_words = ['кто', 'что', 'где', 'когда', 'почему', 'зачем', 'как']
    return any(text.lower().startswith(word) for word in question_words)


def get_random_emoji() -> str:
    """
    Возвращает случайный эмодзи для разнообразия.
    """
    import random
    
    emojis = [
        '🎉', '🎈', '✨', '⭐', '🌟', '🦄', '🧁', '🍰',
        '🎂', '🍪', '☀️', '🌈', '💖', '💕', '😊', '🎊',
        '🎵', '🎶', '🎭', '🎪', '🎨', '🎮', '🎯', '🎲'
    ]
    
    return random.choice(emojis)


def add_random_emoji(text: str, chance: float = 0.3) -> str:
    """
    Добавляет случайный эмодзи в конец текста с заданной вероятностью.
    """
    import random
    
    if not text:
        return text
    
    if random.random() < chance:
        return f"{text} {get_random_emoji()}"
    
    return text


def escape_markdown(text: str) -> str:
    """
    Экранирует спецсимволы Markdown.
    """
    if not text:
        return ""
    
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    
    return text
