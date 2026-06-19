# bot/main.py
"""
Главный файл бота Пинки Пай.
Инициализация и запуск бота с регистрацией всех обработчиков.

Автор: MADAO81
"""

import asyncio
import logging
from umaxbot import Bot, Dispatcher
from bot.config import Config
from bot.handlers import commands_router, messages_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Основная функция запуска бота.
    """
    # Проверка наличия токена
    if not Config.MAX_BOT_TOKEN:
        logger.error("❌ Токен бота не найден! Проверьте .env файл.")
        return
    
    # Инициализация бота
    bot = Bot(token=Config.MAX_BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    dp.include_router(commands_router)
    dp.include_router(messages_router)
    
    # Информация о запуске
    logger.info("🦄 Пинки Пай запускается!")
    logger.info(f"⏰ Рабочие часы: {Config.WORK_HOURS_START}:00 — {Config.WORK_HOURS_END}:00")
    logger.info(f"🎲 Шанс комментария: {int(Config.CHANCE_TO_COMMENT * 100)}%")
    logger.info(f"🧠 ИИ: {'Доступен' if Config.is_ai_available() else 'Недоступен'}")
    logger.info("📝 Автор: MADAO81")
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
