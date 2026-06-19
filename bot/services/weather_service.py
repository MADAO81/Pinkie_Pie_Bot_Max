# bot/services/weather_service.py
"""
Сервис для получения погоды в Боровском районе Калужской области.
Использует Open-Meteo API (бесплатно, без ключа).

Автор: MADAO81
"""

import logging
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any, List

# Настройка логирования
logger = logging.getLogger(__name__)

# Координаты Боровского района Калужской области
BOROVSK_LAT = 55.206
BOROVSK_LON = 36.486

# Open-Meteo API (бесплатный, без ключа)
WEATHER_API_URL = "https://api.open-meteo.com/v1/forecast"

# Кэш для хранения последнего ответа погоды
_weather_cache = {
    'data': None,
    'last_update': None,
    'cache_duration': 1800  # 30 минут
}


async def get_weather() -> Optional[Dict[str, Any]]:
    """
    Получает текущую погоду в Боровском районе через Open-Meteo.
    Возвращает словарь с данными о погоде или None при ошибке.
    """
    # Проверяем кэш
    if _weather_cache['data'] and _weather_cache['last_update']:
        elapsed = (datetime.now() - _weather_cache['last_update']).total_seconds()
        if elapsed < _weather_cache['cache_duration']:
            logger.debug("📦 Использую кэшированные данные погоды")
            return _weather_cache['data']
    
    try:
        async with aiohttp.ClientSession() as session:
            # Параметры запроса к Open-Meteo
            params = {
                'latitude': BOROVSK_LAT,
                'longitude': BOROVSK_LON,
                'current_weather': 'true',
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
                'timezone': 'Europe/Moscow',
                'forecast_days': 1
            }
            
            headers = {
                'User-Agent': 'PinkiePieBot/1.0 (MADAO81)'
            }
            
            async with session.get(WEATHER_API_URL, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Парсим текущую погоду
                    current = data.get('current_weather', {})
                    hourly = data.get('hourly', {})
                    
                    # Находим индекс текущего часа
                    now = datetime.now()
                    current_hour = now.hour
                    
                    # Ищем данные для текущего часа
                    times = hourly.get('time', [])
                    temp_idx = None
                    for i, t in enumerate(times):
                        if t.endswith(f"{current_hour:02d}:00"):
                            temp_idx = i
                            break
                    
                    # Если не нашли точное совпадение, берём первый доступный
                    if temp_idx is None and times:
                        temp_idx = 0
                    
                    # Получаем данные
                    weather_data = {
                        'temperature': current.get('temperature', 0),
                        'weather_code': current.get('weathercode', 0),
                        'wind_speed': current.get('windspeed', 0),
                        'wind_direction': current.get('winddirection', 0),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Добавляем дополнительные данные из почасового прогноза
                    if temp_idx is not None and temp_idx < len(hourly.get('temperature_2m', [])):
                        weather_data['feels_like'] = hourly['temperature_2m'][temp_idx]  # Приблизительно
                        weather_data['humidity'] = hourly.get('relative_humidity_2m', [0])[temp_idx] if hourly.get('relative_humidity_2m') else 0
                        weather_data['precipitation'] = hourly.get('precipitation', [0])[temp_idx] if hourly.get('precipitation') else 0
                    else:
                        weather_data['feels_like'] = weather_data['temperature']
                        weather_data['humidity'] = 0
                        weather_data['precipitation'] = 0
                    
                    # Определяем описание погоды по коду
                    weather_data['weather'] = get_weather_description(weather_data['weather_code'])
                    weather_data['clouds'] = 50  # Open-Meteo не даёт облачность в current_weather
                    
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


async def get_forecast() -> Optional[List[Dict[str, Any]]]:
    """
    Получает прогноз погоды на 24 часа через Open-Meteo.
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'latitude': BOROVSK_LAT,
                'longitude': BOROVSK_LON,
                'hourly': 'temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m',
                'timezone': 'Europe/Moscow',
                'forecast_days': 1
            }
            
            headers = {
                'User-Agent': 'PinkiePieBot/1.0 (MADAO81)'
            }
            
            async with session.get(WEATHER_API_URL, params=params, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    hourly = data.get('hourly', {})
                    
                    if not hourly:
                        return None
                    
                    forecasts = []
                    times = hourly.get('time', [])
                    temps = hourly.get('temperature_2m', [])
                    humidities = hourly.get('relative_humidity_2m', [])
                    precipitations = hourly.get('precipitation', [])
                    weather_codes = hourly.get('weather_code', [])
                    wind_speeds = hourly.get('wind_speed_10m', [])
                    
                    # Берем только ближайшие 8 часов (как в старом коде)
                    for i in range(min(8, len(times))):
                        forecasts.append({
                            'time': times[i] if i < len(times) else '',
                            'temperature': temps[i] if i < len(temps) else 0,
                            'humidity': humidities[i] if i < len(humidities) else 0,
                            'precipitation': precipitations[i] if i < len(precipitations) else 0,
                            'weather': get_weather_description(weather_codes[i] if i < len(weather_codes) else 0),
                            'weather_code': weather_codes[i] if i < len(weather_codes) else 0,
                            'wind_speed': wind_speeds[i] if i < len(wind_speeds) else 0
                        })
                    
                    return forecasts
                    
                else:
                    logger.error(f"❌ Ошибка API прогноза: {response.status}")
                    return None
                    
    except Exception as e:
        logger.error(f"❌ Ошибка при получении прогноза: {e}")
        return None


def get_weather_description(weather_code: int) -> str:
    """
    Возвращает текстовое описание погоды по коду WMO.
    Коды WMO: https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM
    """
    weather_codes = {
        0: "Ясно",
        1: "Преимущественно ясно",
        2: "Переменная облачность",
        3: "Пасмурно",
        45: "Туман",
        48: "Туман с изморозью",
        51: "Морось слабая",
        53: "Морось умеренная",
        55: "Морось сильная",
        56: "Ледяная морось слабая",
        57: "Ледяная морось сильная",
        61: "Дождь слабый",
        63: "Дождь умеренный",
        65: "Дождь сильный",
        66: "Ледяной дождь слабый",
        67: "Ледяной дождь сильный",
        71: "Снег слабый",
        73: "Снег умеренный",
        75: "Снег сильный",
        77: "Снежная крупа",
        80: "Ливень слабый",
        81: "Ливень умеренный",
        82: "Ливень сильный",
        85: "Снегопад слабый",
        86: "Снегопад сильный",
        95: "Гроза",
        96: "Гроза с градом слабая",
        99: "Гроза с градом сильная"
    }
    
    return weather_codes.get(weather_code, "Неизвестно")


def get_weather_emoji(weather_code: int) -> str:
    """
    Возвращает эмодзи для кода погоды WMO.
    """
    # Группируем коды по типам погоды
    if weather_code == 0:
        return "☀️"  # Ясно
    elif weather_code in [1, 2]:
        return "🌤️"  # Малооблачно
    elif weather_code == 3:
        return "☁️"  # Пасмурно
    elif weather_code in [45, 48]:
        return "🌫️"  # Туман
    elif weather_code in [51, 53, 55, 56, 57]:
        return "🌧️"  # Морось
    elif weather_code in [61, 63, 65, 66, 67]:
        return "🌧️"  # Дождь
    elif weather_code in [71, 73, 75, 77, 85, 86]:
        return "❄️"  # Снег
    elif weather_code in [80, 81, 82]:
        return "⛈️"  # Ливень
    elif weather_code in [95, 96, 99]:
        return "⛈️"  # Гроза
    else:
        return "🌤️"  # Другое


def is_bad_weather() -> bool:
    """
    Проверяет, плохая ли сейчас погода.
    Возвращает True, если погода плохая (дождь, снег, пасмурно, туман).
    """
    weather_data = None
    
    # Пытаемся получить погоду синхронно
    try:
        import asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            weather_data = asyncio.run_coroutine_threadsafe(get_weather(), loop).result(timeout=5)
        else:
            weather_data = asyncio.run(get_weather())
    except Exception as e:
        logger.warning(f"⚠️ Не удалось получить погоду для проверки состояния: {e}")
        return False
    
    if not weather_data:
        return False
    
    weather_code = weather_data.get('weather_code', 0)
    precipitation = weather_data.get('precipitation', 0)
    
    # Плохая погода:
    # - Дождь (51-67, 80-82)
    # - Снег (71-77, 85-86)
    # - Туман (45, 48)
    # - Гроза (95-99)
    # - Пасмурно (3)
    # - Или есть осадки (> 0)
    is_rain = 51 <= weather_code <= 67 or 80 <= weather_code <= 82
    is_snow = 71 <= weather_code <= 77 or 85 <= weather_code <= 86
    is_fog = weather_code in [45, 48]
    is_thunder = 95 <= weather_code <= 99
    is_cloudy = weather_code == 3
    has_precipitation = precipitation > 0
    
    return is_rain or is_snow or is_fog or is_thunder or is_cloudy or has_precipitation


def format_weather_message(weather_data: Dict[str, Any]) -> str:
    """
    Форматирует данные о погоде в красивое сообщение.
    """
    if not weather_data:
        return "🌤️ Не удалось получить данные о погоде :("
    
    temp = weather_data.get('temperature', 0)
    feels_like = weather_data.get('feels_like', temp)
    weather_desc = weather_data.get('weather', 'неизвестно')
    weather_code = weather_data.get('weather_code', 0)
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    precipitation = weather_data.get('precipitation', 0)
    
    emoji = get_weather_emoji(weather_code)
    
    message = (
        f"{emoji} *Погода в Боровске*\n\n"
        f"🌡️ Температура: *{temp:.1f}°C*\n"
        f"🤔 Ощущается как: *{feels_like:.1f}°C*\n"
        f"🌤️ Описание: *{weather_desc}*\n"
        f"💧 Влажность: *{humidity}%*\n"
        f"💨 Ветер: *{wind_speed:.1f} м/с*\n"
    )
    
    if precipitation > 0:
        message += f"🌧️ Осадки: *{precipitation:.1f} мм*\n"
    
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


def clear_weather_cache():
    """
    Очищает кэш погоды (для принудительного обновления).
    """
    global _weather_cache
    _weather_cache = {
        'data': None,
        'last_update': None,
        'cache_duration': 1800
    }
    logger.info("🧹 Кэш погоды очищен")
