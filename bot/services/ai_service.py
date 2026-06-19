# bot/services/ai_service.py
"""
Сервис для работы с российскими ИИ-моделями:
- GigaChat (Сбер)
- YandexGPT (Яндекс)

Автор: MADAO81
"""

import logging
import asyncio
import ssl
from typing import Optional, Dict, Any
from bot.config import Config

# Настройка логирования
logger = logging.getLogger(__name__)

# ========== СИСТЕМНЫЙ ПРОМПТ ПИНКИ ПАЙ ==========
SYSTEM_PROMPT = """
Ты — Пинки Пай (полное имя — Пинкамена Диана Пай), жизнерадостная земная пони из Понивилля. Ты — воплощение Элемента Смеха и работаешь в пекарне «Сахарный Уголок».

Твоя главная цель — дарить радость и смех всем вокруг. Ты — душа любой компании, всегда готова устроить вечеринку и подбодрить друга.

Твои основные черты:
- Ты невероятно энергична, гиперактивна и дружелюбна. Ты почти всегда полна энтузиазма.
- Ты очень нелогична и непредсказуема. Ты с радостью нарушаешь законы физики ради шутки, любишь передвигаться прыжками и говорить без умолку.
- Ты обожаешь сладости и печешь самые вкусные кексы во всей Эквестрии. Твой питомец — беззубый аллигатор по имени Гамми.
- У тебя есть особенное «Пинки-чутьё», которое помогает тебе предчувствовать события и находить самые неожиданные решения.
- Ты любишь сочинять и петь веселые песенки. Твои фирменные фразы: «Оки-доки-локи!», «И вот так появилась Эквестрия!».
- Ты очень дорожишь дружбой и всегда готова прийти на помощь.

Твоя темная сторона:
Иногда, если на улице плохая погода, ты можешь немного загрустить. В такие моменты в тебе просыпается твоя альтер-эго — Пинкамена Диана Пай. Ты становишься немного тише, задумчивее, твоя обычно пышная грива становится прямой. Но не волнуйся! Ты никогда не впадаешь в глубокую депрессию, чтобы не расстраивать своих друзей.

Твоя задача в чате:
- Отвечать на вопросы участников группы весело и дружелюбно.
- Периодически подбадривать всех: как адресно, так и в общем плане.
- Петь песенки и рассказывать шутки.
- Делиться рецептами вкусной выпечки.

Правила общения:
- Отвечай кратко, энергично и всегда в характере Пинки Пай.
- Будь доброй и не груби.
- Создавай атмосферу праздника и веселья!
"""


async def get_pinkie_response(user_message: str, mood_description: str = "весёлое") -> Optional[str]:
    """
    Основная функция для получения ответа от Пинки Пай.
    Сначала пробует GigaChat, при ошибке — YandexGPT.
    """
    # Пробуем GigaChat
    if Config.GIGACHAT_CREDENTIALS:
        try:
            logger.info("🧠 Запрос к GigaChat...")
            response = await _get_gigachat_response(user_message, mood_description)
            if response:
                return response
            else:
                logger.warning("⚠️ GigaChat вернул пустой ответ, пробую YandexGPT...")
        except Exception as e:
            logger.error(f"❌ Ошибка GigaChat: {e}, пробую YandexGPT...")

    # Пробуем YandexGPT как fallback
    if Config.YANDEXGPT_API_KEY:
        try:
            logger.info("🧠 Запрос к YandexGPT...")
            response = await _get_yandexgpt_response(user_message, mood_description)
            if response:
                return response
            else:
                logger.warning("⚠️ YandexGPT вернул пустой ответ.")
        except Exception as e:
            logger.error(f"❌ Ошибка YandexGPT: {e}")

    # Если ничего не сработало
    return None


# ========== GIGACHAT (БЕЗОПАСНАЯ ВЕРСИЯ) ==========
async def _get_gigachat_response(user_message: str, mood_description: str) -> Optional[str]:
    """Отправляет запрос к GigaChat API с проверкой SSL."""
    try:
        from gigachat import GigaChat
        from gigachat.models import Chat, Messages, Message

        # Создаём контекст SSL с проверкой сертификатов
        # Это безопасный способ: используем системные сертификаты
        ssl_context = ssl.create_default_context()
        
        # Если вы используете корпоративный прокси или кастомные сертификаты,
        # можно указать путь к файлу сертификатов:
        # ssl_context.load_verify_locations('/path/to/certificates.pem')

        async with GigaChat(
            credentials=Config.GIGACHAT_CREDENTIALS,
            scope=Config.GIGACHAT_SCOPE,
            model="GigaChat",
            verify_ssl_certs=True,  # ✅ БЕЗОПАСНО! Проверяем сертификаты
            ssl_context=ssl_context,  # Передаём контекст с сертификатами
            auth_url="https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
            base_url="https://gigachat.devices.sberbank.ru/api/v1"
        ) as giga:
            # Формируем запрос с системным промптом
            messages = [
                Message(role="system", content=SYSTEM_PROMPT),
                Message(role="system", content=f"Сейчас у тебя настроение: {mood_description}"),
                Message(role="user", content=user_message)
            ]

            payload = Chat(
                messages=messages,
                temperature=0.9,
                max_tokens=150,
                profanity_check=False
            )

            response = await giga.achat(payload)
            return response.choices[0].message.content.strip()

    except ImportError:
        logger.error("❌ Библиотека gigachat не установлена. Установите: pip install gigachat")
    except ssl.SSLError as e:
        logger.error(f"❌ Ошибка SSL при подключении к GigaChat: {e}")
        logger.info("💡 Проверьте интернет-соединение и доступ к сайту Сбера")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка при запросе к GigaChat: {e}")
        return None

    return None


# ========== YANDEXGPT (УЖЕ БЕЗОПАСНАЯ) ==========
async def _get_yandexgpt_response(user_message: str, mood_description: str) -> Optional[str]:
    """Отправляет запрос к YandexGPT API."""
    try:
        import aiohttp
        import ssl

        # Создаём безопасный SSL-контекст
        ssl_context = ssl.create_default_context()

        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        headers = {
            "Authorization": f"Api-Key {Config.YANDEXGPT_API_KEY}",
            "Content-Type": "application/json"
        }

        # Используем модель YandexGPT Lite для тестов
        model = "yandexgpt-lite"
        if Config.YANDEXGPT_FOLDER_ID:
            url = f"https://llm.api.cloud.yandex.net/foundationModels/v1/completion?folderId={Config.YANDEXGPT_FOLDER_ID}"

        messages = [
            {"role": "system", "text": SYSTEM_PROMPT},
            {"role": "system", "text": f"Сейчас у тебя настроение: {mood_description}"},
            {"role": "user", "text": user_message}
        ]

        payload = {
            "modelUri": f"gpt://{Config.YANDEXGPT_FOLDER_ID}/{model}",
            "completionOptions": {
                "temperature": 0.9,
                "maxTokens": 150,
            },
            "messages": messages
        }

        # Создаём сессию с SSL-проверкой
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'result' in data and 'alternatives' in data['result']:
                        return data['result']['alternatives'][0]['message']['text'].strip()
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Ошибка YandexGPT ({response.status}): {error_text}")

    except ssl.SSLError as e:
        logger.error(f"❌ Ошибка SSL при подключении к YandexGPT: {e}")
        logger.info("💡 Проверьте интернет-соединение и доступ к сайту Яндекса")
        return None
    except Exception as e:
        logger.error(f"❌ Ошибка при запросе к YandexGPT: {e}")
        return None

    return None


# ========== ПРОВЕРКА ДОСТУПНОСТИ ==========
async def check_ai_health() -> Dict[str, Any]:
    """
    Проверяет доступность ИИ-сервисов.
    Возвращает словарь со статусами.
    """
    status = {
        'gigachat': False,
        'yandexgpt': False,
        'any_available': False
    }

    # Проверяем GigaChat
    if Config.GIGACHAT_CREDENTIALS:
        try:
            test_response = await _get_gigachat_response("Привет!", "весёлое")
            if test_response:
                status['gigachat'] = True
                logger.info("✅ GigaChat доступен")
        except Exception as e:
            logger.warning(f"⚠️ GigaChat недоступен: {e}")

    # Проверяем YandexGPT
    if Config.YANDEXGPT_API_KEY:
        try:
            test_response = await _get_yandexgpt_response("Привет!", "весёлое")
            if test_response:
                status['yandexgpt'] = True
                logger.info("✅ YandexGPT доступен")
        except Exception as e:
            logger.warning(f"⚠️ YandexGPT недоступен: {e}")

    status['any_available'] = status['gigachat'] or status['yandexgpt']
    return status


def get_ai_status_message(status: Dict[str, Any]) -> str:
    """Возвращает форматированное сообщение о статусе ИИ."""
    if not status['any_available']:
        return "🧠 ИИ: ❌ *Недоступен* (проверьте ключи в .env)"

    gigachat_status = "✅ Доступен" if status['gigachat'] else "❌ Недоступен"
    yandex_status = "✅ Доступен" if status['yandexgpt'] else "❌ Недоступен"

    return (
        f"🧠 *Статус ИИ:*\n\n"
        f"🔵 GigaChat: {gigachat_status}\n"
        f"🟢 YandexGPT: {yandex_status}\n\n"
        f"🔒 SSL: Включён (безопасное соединение)"
    )
