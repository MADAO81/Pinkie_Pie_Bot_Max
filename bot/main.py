import asyncio
import logging
from umaxbot import Bot, Dispatcher
from bot.config import Config
from bot.handlers import commands, messages

# Настройка логирования
logging.basicConfig(level=logging.INFO)

async def main():
    # Инициализация бота
    bot = Bot(token=Config.MAX_BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация обработчиков
    dp.include_router(commands.router)
    dp.include_router(messages.router)
    
    # Запуск polling
    print("🦄 Пинки Пай запускается!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())