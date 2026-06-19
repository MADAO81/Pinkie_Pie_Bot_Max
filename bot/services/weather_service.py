# bot/services/weather_service.py
"""
Сервис для получения погоды в Боровском районе Калужской области.
Использует OpenWeatherMap API.

Автор: MADAO81
"""

import os
import logging
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any
from bot.config import Config

# Настройка логирования
logger = logging.getLogger(__name__)

# Координаты Боровского района Калужской области
BOROVSK_LAT = 55.206
BOROVSK_LON = 36.486

# OpenWeatherMap API
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Кэш для хранения последнего ответа погоды
_weather_cache = {
    'data': None,
    'last_update': None,
    'cache_duration': 1800  # 30 минут
}


async def get_weather() -> Optional[Dict[str, Any]]:
    """
    Получает текущую погоду в Боровском районе.
    Возвращает словарь с данными о погоде или None при ошибке.
    """
    api_key = Config.WEATHER_API_KEY
    
    if not api_key:
        logger.warning("⚠️ WEATHER_API_KEY не найден в .env!")
        return None
    
    # Проверяем кэш
    if _weather_cache['data'] and _weather_cache['last_update']:
        elapsed = (datetime.now() - _weather_cache['last_update']).total_seconds()
        if elapsed < _weather_cache['cache_duration']:
            logger.debug("📦 Использую кэшированные данные погоды")
            return _weather_cache['data']
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'lat': BOROVSK_LAT,
                'lon': BOROVSK_LON,
                'appid': api_key,
                'units': 'metric',
                'lang': 'ru'
            }
            
            async with session.get(WEATHER_API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Парсим нужные данные
                    weather_data = {
                        'temperature': data['main']['temp'],
                        'feels_like': data['main']['feels_like'],
                        'humidity': data['main']['humidity'],
                        'pressure': data['main']['pressure'],
                        'weather': data['weather'][0]['description'],
                        'weather_code': data['weather'][0]['id'],
                        'wind_speed': data['wind']['speed'],
                        'clouds': data['clouds']['all'],
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Обновляем кэш
                    _weather_cache['data'] = weather_data
                    _weather_cache['last_update'] = datetime.now()
                    
                    logger.info(f"🌤️ Погода в Боровске: {weather_data['temperature']}°C, {weather_data['weather']}")
                    return weather_data
                else:
                    logger.error(f"❌ Ошибка API погоды: {response.status}")
                    return None
                    
    except aiohttp.ClientError as e:
        logger.error(f"❌ Ошибка соединения с API погоды: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Неизвестная ошибка при получении погоды: {e}")
        return None


async def get_forecast() -> Optional[list]:
    """
    Получает прогноз погоды на 5 дней.
    """
    api_key = Config.WEATHER_API_KEY
    
    if not api_key:
        return None
    
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'lat': BOROVSK_LAT,
                'lon': BOROVSK_LON,
                'appid': api_key,
                'units': 'metric',
                'lang': 'ru',
                'cnt': 8  # 8 периодов по 3 часа = 24 часа
            }
            
            async with session.get(FORECAST_API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    forecasts = []
                    
                    for item in data['list'][:8]:  # Берем только первые 8 записей (24 часа)
                        forecasts.append({
                            'time': item['dt_txt'],
                            'temperature': item['main']['temp'],
                            'weather': item['weather'][0]['description'],
                            'weather_code': item['weather'][0]['id'],
                            'wind_speed': item['wind']['speed'],
                            'clouds': item['clouds']['all']
                        })
                    
                    return forecasts
                else:
                    logger.error(f"❌ Ошибка API прогноза: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"❌ Ошибка при получении прогноза: {e}")
        return None


def is_bad_weather() -> bool:
    """
    Проверяет, плохая ли сейчас погода (дождь, пасмурно, осадки).
    Возвращает True, если погода плохая.
    """
    weather_data = None
    
    # Пытаемся получить погоду синхронно (для использования в других функциях)
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если мы уже в асинхронном контексте, создаём новую задачу
            weather_data = asyncio.run_coroutine_threadsafe(get_weather(), loop).result()
        else:
            weather_data = asyncio.run(get_weather())
    except:
        logger.warning("⚠️ Не удалось получить погоду для проверки состояния")
        return False
    
    if not weather_data:
        return False
    
    # Проверяем код погоды
    # 500-599 - дождь
    # 600-699 - снег
    # 700-799 - туман/дымка
    # 800 - ясно
    # 801-804 - облачность (801 - мало, 804 - пасмурно)
    weather_code = weather_data.get('weather_code', 800)
    clouds = weather_data.get('clouds', 0)
    
    # Плохая погода: дождь, снег, пасмурно (облачность > 60%)
    is_rain = 500 <= weather_code <= 599
    is_snow = 600 <= weather_code <= 699
    is_fog = 700 <= weather_code <= 799
    is_cloudy = 801 <= weather_code <= 804 and clouds > 60
    
    return is_rain or is_snow or is_fog or is_cloudy


def get_weather_emoji(weather_code: int) -> str:
    """
    Возвращает эмодзи для кода погоды.
    """
    if 200 <= weather_code <= 232:
        return "⛈️"  # Гроза
    elif 300 <= weather_code <= 321:
        return "🌧️"  # Морось
    elif 500 <= weather_code <= 531:
        return "🌧️"  # Дождь
    elif 600 <= weather_code <= 622:
        return "❄️"  # Снег
    elif 700 <= weather_code <= 781:
        return "🌫️"  # Туман
    elif weather_code == 800:
        return "☀️"  # Ясно
    elif 801 <= weather_code <= 804:
        return "☁️"  # Облачно
    else:
        return "🌤️"  # Другое


def format_weather_message(weather_data: Dict[str, Any]) -> str:
    """
    Форматирует данные о погоде в красивое сообщение.
    """
    if not weather_data:
        return "🌤️ Не удалось получить данные о погоде :("
    
    temp = weather_data.get('temperature', 0)
    feels_like = weather_data.get('feels_like', 0)
    weather_desc = weather_data.get('weather', 'неизвестно')
    weather_code = weather_data.get('weather_code', 800)
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    
    emoji = get_weather_emoji(weather_code)
    
    message = (
        f"{emoji} *Погода в Боровске*\n\n"
        f"🌡️ Температура: *{temp:.1f}°C*\n"
        f"🤔 Ощущается как: *{feels_like:.1f}°C*\n"
        f"🌤️ Описание: *{weather_desc.capitalize()}*\n"
        f"💧 Влажность: *{humidity}%*\n"
        f"💨 Ветер: *{wind_speed:.1f} м/с*\n"
    )
    
    return message


def get_weather_mood_influence() -> dict:
    """
    Возвращает влияние погоды на настроение.
    Используется в системе настроений Пинки Пай.
    """
    is_bad = is_bad_weather()
    
    if is_bad:
        return {
            'mood_shift': 'pinkamena',
            'chance': 0.20,  # 20% шанс на грусть
            'reason': 'на улице дождь и пасмурно 🌧️'
        }
    else:
        return {
            'mood_shift': 'happy',
            'chance': 0.80,
            'reason': 'погода радует нас солнышком ☀️'
        }
