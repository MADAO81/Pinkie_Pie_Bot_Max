# bot/core/stats_manager.py
"""
Управление статистикой бота.
Сохранение и загрузка данных в JSON-файл.

Автор: MADAO81
"""

import json
import os
from datetime import datetime
from bot.core.constants import WEEKLY_JOKE_LIMIT

# Путь к файлу статистики
STATS_FILE = 'data/stats.json'


def load_stats() -> dict:
    """
    Загружает статистику из файла.
    Если файла нет — создаёт новую структуру.
    """
    # Создаём папку data, если её нет
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    
    try:
        with open(STATS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Создаём новую статистику
        return {
            'week_start': datetime.now().strftime('%Y-%m-%d'),
            'jokes_count': 0,
            'total_jokes': 0,
            'last_joke_time': None,
            'last_recipe_date': None,
            'users_interacted': [],
            'mood_stats': {}
        }


def save_stats(stats: dict):
    """
    Сохраняет статистику в файл.
    """
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def can_joke(stats: dict) -> bool:
    """
    Проверяет, можно ли пошутить.
    Учитывает недельный лимит и кулдаун между шутками.
    """
    # Проверяем недельный сброс
    week_start = datetime.strptime(stats['week_start'], '%Y-%m-%d').date()
    today = datetime.now().date()
    
    # Если прошла неделя — сбрасываем счётчик
    if (today - week_start).days >= 7:
        stats['week_start'] = today.strftime('%Y-%m-%d')
        stats['jokes_count'] = 0
        save_stats(stats)
    
    # Проверяем лимит
    if stats['jokes_count'] >= WEEKLY_JOKE_LIMIT:
        return False
    
    # Проверяем кулдаун между шутками
    if stats.get('last_joke_time'):
        try:
            last_joke = datetime.fromisoformat(stats['last_joke_time'])
            from bot.core.constants import COOLDOWN_MINUTES
            if (datetime.now() - last_joke).total_seconds() < COOLDOWN_MINUTES * 60:
                return False
        except (ValueError, TypeError):
            # Если дата кривая — пропускаем проверку
            pass
    
    return True


def register_joke(stats: dict, mood=None):
    """
    Регистрирует шутку в статистике.
    """
    stats['jokes_count'] = stats.get('jokes_count', 0) + 1
    stats['total_jokes'] = stats.get('total_jokes', 0) + 1
    stats['last_joke_time'] = datetime.now().isoformat()
    
    # Сохраняем статистику по настроениям
    if mood:
        mood_name = mood.value if hasattr(mood, 'value') else str(mood)
        if 'mood_stats' not in stats:
            stats['mood_stats'] = {}
        stats['mood_stats'][mood_name] = stats['mood_stats'].get(mood_name, 0) + 1
    
    save_stats(stats)


def register_user(stats: dict, user_id: int, username: str = None):
    """
    Регистрирует взаимодействие с пользователем.
    """
    if 'users_interacted' not in stats:
        stats['users_interacted'] = []
    
    # Формируем данные пользователя
    user_data = {
        'id': user_id,
        'username': username,
        'last_active': datetime.now().isoformat()
    }
    
    # Обновляем существующего пользователя
    for i, user in enumerate(stats['users_interacted']):
        if user['id'] == user_id:
            stats['users_interacted'][i]['last_active'] = datetime.now().isoformat()
            if username:
                stats['users_interacted'][i]['username'] = username
            save_stats(stats)
            return
    
    # Добавляем нового пользователя
    stats['users_interacted'].append(user_data)
    save_stats(stats)


def get_user_stats(stats: dict, user_id: int) -> dict:
    """
    Возвращает статистику по конкретному пользователю.
    """
    for user in stats.get('users_interacted', []):
        if user['id'] == user_id:
            return user
    return None


def reset_weekly_stats(stats: dict):
    """
    Принудительный сброс недельной статистики.
    """
    stats['week_start'] = datetime.now().strftime('%Y-%m-%d')
    stats['jokes_count'] = 0
    save_stats(stats)
