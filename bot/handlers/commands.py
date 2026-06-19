# bot/handlers/commands.py
"""
Обработчики команд для бота Пинки Пай.
Содержит все команды: /start, /help, /stats, /mood, /recipe.

Автор: MADAO81
"""

import random
from datetime import datetime
from umaxbot import Router, types
from bot.config import Config
from bot.core.stats_manager import load_stats, register_user
from bot.core.mood_system import get_pinkie_mood, get_mood_description, get_mood_advice
from bot.core.constants import WEEKLY_JOKE_LIMIT
from bot.services.recipe_service import get_daily_recipe

router = Router()


@router.message(commands=['start'])
async def start_command(message: types.Message):
    """
    Обработчик команды /start.
    Приветствует пользователя и показывает основную информацию.
    """
    stats = load_stats()
    register_user(stats, message.sender.id, message.sender.username)
    
    mood, mood_desc = get_pinkie_mood()
    
    # Формируем приветственное сообщение
    await message.answer(
        f"🦄 *Пинки Пай приветствует тебя!*\n\n"
        f"Моё настроение: {mood_desc}\n"
        f"Работаю с {Config.WORK_HOURS_START}:00 до {Config.WORK_HOURS_END}:00 ежедневно 🌞\n"
        f"Шанс шутки: {int(Config.CHANCE_TO_COMMENT * 100)}%\n"
        f"Всего шуток: {stats.get('total_jokes', 0)}\n\n"
        f"📝 Команды:\n"
        f"/stats — статистика\n"
        f"/mood — настроение\n"
        f"/recipe — рецепт дня\n"
        f"/help — помощь",
        parse_mode='Markdown'
    )


@router.message(commands=['help'])
async def help_command(message: types.Message):
    """
    Обработчик команды /help.
    Показывает список всех команд и правил общения.
    """
    ai_status = "включён" if Config.is_ai_available() else "отключён"
    
    await message.answer(
        f"🦄 *Команды Пинки Пай:*\n\n"
        f"✨ /start — приветствие\n"
        f"📊 /stats — статистика шуток\n"
        f"🎭 /mood — текущее настроение\n"
        f"🧁 /recipe — рецепт дня\n"
        f"❓ /help — эта справка\n\n"
        f"*Как общаться:*\n"
        f"• Просто упомяни меня (@{message.bot.username}) в сообщении\n"
        f"• Или скажи слово 'Пинки' — я отвечу!\n\n"
        f"*Дополнительно:*\n"
        f"⏰ Работаю с {Config.WORK_HOURS_START}:00 до {Config.WORK_HOURS_END}:00\n"
        f"🎲 Могу случайно прокомментировать любое сообщение ({int(Config.CHANCE_TO_COMMENT * 100)}%)\n"
        f"🧠 ИИ: {ai_status}\n"
        f"📊 Лимит шуток: {WEEKLY_JOKE_LIMIT} в неделю\n\n"
        f"*Приятного общения!* 🎈",
        parse_mode='Markdown'
    )


@router.message(commands=['stats'])
async def stats_command(message: types.Message):
    """
    Обработчик команды /stats.
    Показывает статистику шуток и взаимодействий.
    """
    stats = load_stats()
    register_user(stats, message.sender.id, message.sender.username)
    
    # Расчёт оставшихся шуток
    week_start = datetime.strptime(stats['week_start'], '%Y-%m-%d').date()
    today = datetime.now().date()
    days_left = 7 - (today - week_start).days
    remaining = max(0, WEEKLY_JOKE_LIMIT - stats.get('jokes_count', 0))
    
    # Статистика по настроениям
    mood_stats = stats.get('mood_stats', {})
    if mood_stats:
        mood_report = "\n".join([f"  - {mood}: {count} шуток" for mood, count in mood_stats.items()])
    else:
        mood_report = "  - пока нет данных"
    
    await message.answer(
        f"📊 *Статистика Пинки Пай*\n\n"
        f"Шуток на этой неделе: {stats.get('jokes_count', 0)}/{WEEKLY_JOKE_LIMIT}\n"
        f"Осталось: {remaining}\n"
        f"Дней до сброса: {days_left}\n"
        f"Всего шуток за всё время: {stats.get('total_jokes', 0)}\n"
        f"Пользователей обслужено: {len(stats.get('users_interacted', []))}\n\n"
        f"*Распределение по настроениям:*\n{mood_report}",
        parse_mode='Markdown'
    )


@router.message(commands=['mood'])
async def mood_command(message: types.Message):
    """
    Обработчик команды /mood.
    Показывает текущее настроение Пинки Пай.
    """
    mood, mood_desc = get_pinkie_mood()
    advice = get_mood_advice(mood)
    
    await message.answer(
        f"🎭 *Моё настроение сейчас:*\n{mood_desc}\n\n"
        f"💡 *Совет:* {advice}",
        parse_mode='Markdown'
    )


@router.message(commands=['recipe'])
async def recipe_command(message: types.Message):
    """
    Обработчик команды /recipe.
    Показывает рецепт дня с andychef.ru.
    """
    stats = load_stats()
    today = datetime.now().date()
    
    # Проверяем, не давали ли рецепт сегодня
    last_recipe = stats.get('last_recipe_date')
    if last_recipe and last_recipe == today.isoformat():
        await message.answer(
            "🧁 *Ой-ой!* Я уже делилась рецептом сегодня!\n"
            "Приходи завтра — будет новый кекс! 🎂",
            parse_mode='Markdown'
        )
        return
    
    # Показываем, что бот "думает"
    await message.answer("🔍 *Ищу вкусный рецепт...*", parse_mode='Markdown')
    
    # Получаем рецепт
    recipe = await get_daily_recipe()
    
    if recipe:
        # Сохраняем дату выдачи рецепта
        stats['last_recipe_date'] = today.isoformat()
        save_stats(stats)
        
        await message.answer(
            f"🧁 *Рецепт дня от Пинки Пай!*\n\n{recipe}\n\n"
            f"*Приятного аппетита!* 🥄",
            parse_mode='Markdown'
        )
    else:
        await message.answer(
            "😅 *Ой!* Сегодня я не нашла рецепт на сайте.\n"
            "Давайте просто устроим вечеринку! 🎉",
            parse_mode='Markdown'
        )


# Вспомогательная функция для импорта в других модулях
def get_router():
    """Возвращает роутер для регистрации в основном приложении."""
    return router
