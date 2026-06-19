import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Токен MAX
    MAX_BOT_TOKEN = os.getenv('MAX_BOT_TOKEN')
    
    # GigaChat
    GIGACHAT_CREDENTIALS = os.getenv('GIGACHAT_CREDENTIALS')
    GIGACHAT_SCOPE = os.getenv('GIGACHAT_SCOPE', 'GIGACHAT_API_PERS')
    
    # YandexGPT
    YANDEXGPT_API_KEY = os.getenv('YANDEXGPT_API_KEY')
    YANDEXGPT_FOLDER_ID = os.getenv('YANDEXGPT_FOLDER_ID')
    
    # Погода
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    
    # Настройки бота
    WORK_HOURS_START = 9
    WORK_HOURS_END = 20
    CHANCE_TO_COMMENT = 0.20  # 20%
    WEEKLY_JOKE_LIMIT = 30
    RESPONSE_COOLDOWN = 30  # секунд
    
    # Файлы
    STATS_FILE = 'data/stats.json'
    
    # Проверка наличия токенов
    @classmethod
    def is_ai_available(cls):
        return bool(cls.GIGACHAT_CREDENTIALS or cls.YANDEXGPT_API_KEY)