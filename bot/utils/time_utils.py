# bot/utils/time_utils.py
"""
Утилиты для работы со временем и датами.
Проверка рабочих часов, кулдаунов и форматирование времени.

Автор: MADAO81
"""

from datetime import datetime, time, timedelta
from bot.core.constants import WORK_HOURS_START, WORK_HOURS_END, RESPONSE_COOLDOWN

# Глобальная переменная для кулдауна
_last_response_time = None


def is_working_hours() -> bool:
    """
    Проверяет, сейчас рабочие часы.
    Возвращает True, если текущее время входит в рабочий диапазон.
    """
    now = datetime.now()
    current_time = now.time()
    
    # Создаём объекты времени для начала и конца рабочего дня
    start = time(WORK_HOURS_START, 0)
    end = time(WORK_HOURS_END, 0)
    
    return start <= current_time <= end


def is_weekend() -> bool:
    """
    Проверяет, является ли сегодня выходным днём.
    Возвращает True для субботы и воскресенья.
    """
    return datetime.now().weekday() in [5, 6]


def get_working_hours_status() -> dict:
    """
    Возвращает детальный статус рабочего времени.
    """
    now = datetime.now()
    current_time = now.time()
    start = time(WORK_HOURS_START, 0)
    end = time(WORK_HOURS_END, 0)
    
    is_working = start <= current_time <= end
    is_weekend_day = now.weekday() in [5, 6]
    
    # Вычисляем время до конца/начала работы
    if is_working:
        end_datetime = datetime.combine(now.date(), end)
        time_left = end_datetime - now
        hours_left = time_left.seconds // 3600
        minutes_left = (time_left.seconds % 3600) // 60
        time_to = f"{hours_left}ч {minutes_left}мин"
        status = f"⏰ Работаю! До конца смены {time_to}"
    else:
        if current_time < start:
            start_datetime = datetime.combine(now.date(), start)
            time_to_start = start_datetime - now
            hours_to = time_to_start.seconds // 3600
            minutes_to = (time_to_start.seconds % 3600) // 60
            status = f"⏰ Начну работу через {hours_to}ч {minutes_to}мин"
        else:
            # Уже после работы
            tomorrow = now + timedelta(days=1)
            start_datetime = datetime.combine(tomorrow.date(), start)
            time_to_start = start_datetime - now
            hours_to = time_to_start.seconds // 3600
            minutes_to = (time_to_start.seconds % 3600) // 60
            status = f"⏰ Уже отдыхаю! Вернусь через {hours_to}ч {minutes_to}мин"
    
    return {
        'is_working': is_working,
        'is_weekend': is_weekend_day,
        'status': status,
        'current_time': now.strftime('%H:%M'),
        'work_start': f"{WORK_HOURS_START}:00",
        'work_end': f"{WORK_HOURS_END}:00"
    }


def can_respond() -> bool:
    """
    Проверяет, можно ли отвечать (кулдаун между ответами).
    """
    global _last_response_time
    
    if _last_response_time is None:
        return True
    
    elapsed = (datetime.now() - _last_response_time).total_seconds()
    return elapsed >= RESPONSE_COOLDOWN


def update_response_time():
    """
    Обновляет время последнего ответа.
    """
    global _last_response_time
    _last_response_time = datetime.now()


def get_time_until_next_work() -> str:
    """
    Возвращает время до следующего рабочего дня в читаемом формате.
    """
    now = datetime.now()
    start = time(WORK_HOURS_START, 0)
    
    # Если сейчас до начала работы
    if now.time() < start:
        start_datetime = datetime.combine(now.date(), start)
        time_left = start_datetime - now
    else:
        # Если после работы — ждём завтра
        tomorrow = now + timedelta(days=1)
        start_datetime = datetime.combine(tomorrow.date(), start)
        time_left = start_datetime - now
    
    hours = time_left.seconds // 3600
    minutes = (time_left.seconds % 3600) // 60
    
    if hours > 0:
        return f"{hours}ч {minutes}мин"
    return f"{minutes}мин"


def format_timestamp(timestamp: str) -> str:
    """
    Форматирует ISO-строку времени в читаемый вид.
    """
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime('%d.%m.%Y %H:%M')
    except (ValueError, TypeError):
        return "неизвестно"


def get_week_day_name(weekday: int) -> str:
    """
    Возвращает название дня недели на русском.
    """
    days = [
        'Понедельник', 'Вторник', 'Среда',
        'Четверг', 'Пятница', 'Суббота', 'Воскресенье'
    ]
    return days[weekday] if 0 <= weekday < 7 else "неизвестно"


def is_time_to_sing() -> bool:
    """
    Проверяет, не пора ли спеть песенку.
    Случайный фактор + привязка к времени (утром и вечером чаще).
    """
    import random
    hour = datetime.now().hour
    
    # Утром (9-11) и вечером (17-19) поём чаще
    if (9 <= hour <= 11) or (17 <= hour <= 19):
        return random.random() < 0.25  # 25%
    
    return random.random() < 0.10  # 10%


def get_time_greeting() -> str:
    """
    Возвращает приветствие в зависимости от времени суток.
    """
    hour = datetime.now().hour
    
    if 6 <= hour < 12:
        return "Доброе утро!"
    elif 12 <= hour < 18:
        return "Добрый день!"
    elif 18 <= hour < 23:
        return "Добрый вечер!"
    else:
        return "Доброй ночи!"
