# bot/handlers/messages.py
"""
Основной обработчик текстовых сообщений для бота Пинки Пай.
Управляет логикой ответов, триггерами и случайными комментариями.

Автор: MADAO81
"""

import random
import logging
from umaxbot import Router, types
from bot.config import Config
from bot.core.stats_manager import load_stats, register_user, can_joke, register_joke, save_stats
from bot.core.mood_system import get_pinkie_mood, PinkieMood
from bot.core.triggers import get_trigger_reaction, PINKIE_TRIGGERS
from bot.core.constants import TRIGGER_WORDS
from bot.services.ai_service import get_pinkie_response
from bot.utils.time_utils import is_working_hours, can_respond, update_response_time

# Настройка логирования
logger = logging.getLogger(__name__)
router = Router()


@router.message()
async def handle_message(message: types.Message):
    """
    Основной обработчик всех текстовых сообщений.
    """
    # === 1. Базовые проверки ===
    
    # Игнорируем свои сообщения
    if message.sender.id == message.bot.id:
        return
    
    # Игнорируем сообщения без текста
    if not message.text:
        return
    
    # Проверяем рабочие часы
    if not is_working_hours():
        await message.answer(
            "⏰ *Пинки ушла печь кексы!* 🌙\n"
            f"Вернусь завтра в {Config.WORK_HOURS_START}:00 утра!\n"
            "Сладких снов! 🛌",
            parse_mode='Markdown'
        )
        return
    
    # Загружаем статистику
    stats = load_stats()
    register_user(stats, message.sender.id, message.sender.username)
    
    # Получаем текст сообщения
    text = message.text.lower()
    chat_id = message.chat.id
    
    # === 2. Проверка на упоминание и триггеры ===
    
    # Проверяем, позвали ли Пинки
    is_mentioned = "пинки" in text or "@" + message.bot.username in text
    
    # Проверяем триггерные слова
    has_trigger = any(word in text for word in TRIGGER_WORDS)
    
    # === 3. Кулдаун ===
    
    # Если бота не звали и нет триггера — проверяем кулдаун
    if not (is_mentioned or has_trigger):
        if not can_respond():
            logger.debug(f"Кулдаун, пропускаю сообщение: {text[:30]}...")
            return
    
    # Получаем текущее настроение (с учётом погоды)
    mood, mood_desc = get_pinkie_mood()
    
    # === 4. Логика ответов ===
    
    # 4.1. Если позвали или есть триггер — отвечаем всегда
    if is_mentioned or has_trigger:
        logger.info(f"📨 Реакция на упоминание/триггер: {text[:50]}...")
        
        # Проверяем триггерную реакцию
        reaction = get_trigger_reaction(text, mood)
        if reaction:
            await message.answer(
                f"🦄 *Пинки Пай:* {reaction}",
                parse_mode='Markdown'
            )
            update_response_time()
            return
        
        # Если ИИ доступен — используем его
        if Config.is_ai_available():
            logger.info("🧠 Запрос к ИИ...")
            response = await get_pinkie_response(text, mood_desc)
            await message.answer(
                f"🦄 *Пинки Пай:* {response}",
                parse_mode='Markdown'
            )
            update_response_time()
            return
        
        # Если ИИ нет — простой ответ
        await message.answer(
            f"🦄 *Пинки Пай:* Привет! Как настроение? 🎉",
            parse_mode='Markdown'
        )
        update_response_time()
        return
    
    # 4.2. С вероятностью 20% комментируем случайные сообщения
    if random.random() < Config.CHANCE_TO_COMMENT and can_joke(stats):
        logger.info(f"📨 Случайный комментарий (20%): {text[:30]}...")
        
        # Получаем комментарий в зависимости от настроения
        comment = await get_random_comment(mood)
        
        await message.answer(
            f"🦄 *Пинки Пай:* {comment}",
            parse_mode='Markdown'
        )
        register_joke(stats, mood)
        update_response_time()
        return
    
    # 4.3. Если ничего не сработало — молчим
    logger.debug(f"🔇 Бот молчит: {text[:30]}...")


async def get_random_comment(mood: PinkieMood) -> str:
    """
    Возвращает случайный комментарий в зависимости от настроения.
    """
    comments = {
        PinkieMood.HAPPY: [
            "Какой замечательный день! А у вас есть кексы? 🧁",
            "Вы такие классные! Давайте дружить! 🌈",
            "Ура! Я так рада видеть вас в чате! 🎉",
            "Оки-доки-локи! Как дела у моих любимых друзей?",
            "Знаете, что сегодня нужно? Вечеринка! 🎈"
        ],
        PinkieMood.PINKAMENA: [
            "Сегодня пасмурно, но я всё равно рада вас видеть... 🌧️",
            "Мне немного грустно, но кексы всё исправят!",
            "Давайте посидим тихонько и помечтаем о солнышке...",
            "Я тут подумала... А вы любите дождь?",
            "Хочется уюта и тепла. И друзей рядом!"
        ],
        PinkieMood.SILLY: [
            "Я сегодня просто сумасшедшая! Давайте прыгать! 🤪",
            "Знаете, как пахнут кексы? Как счастье!",
            "У меня идея! Давайте устроим самый глупый праздник!",
            "Я тут подумала... А что если у пони будут роллы?",
            "Сегодня я буду петь! Ля-ля-ля! 🎵"
        ]
    }
    
    # Получаем список комментариев для настроения
    mood_comments = comments.get(mood, comments[PinkieMood.HAPPY])
    return random.choice(mood_comments)


def get_router():
    """Возвращает роутер для регистрации в основном приложении."""
    return router
