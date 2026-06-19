# bot/services/recipe_service.py
"""
Сервис для парсинга рецептов с сайта andychef.ru.
Позволяет получать случайные рецепты выпечки.

Автор: MADAO81
"""

import re
import logging
import random
import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from bot.core.stats_manager import load_stats, save_stats

# Настройка логирования
logger = logging.getLogger(__name__)

# Базовый URL сайта
BASE_URL = "https://andychef.ru"
RECIPES_URL = f"{BASE_URL}/category/deserts/"

# Кэш для рецептов
_recipe_cache = {
    'recipes': [],
    'last_update': None,
    'cache_duration': 86400  # 24 часа
}


async def get_random_recipe() -> Optional[Dict[str, str]]:
    """
    Получает случайный рецепт с andychef.ru.
    Возвращает словарь с названием, ингредиентами и инструкцией.
    """
    try:
        # Получаем список рецептов
        recipes = await get_recipe_list()
        
        if not recipes:
            logger.warning("⚠️ Не удалось получить список рецептов")
            return None
        
        # Выбираем случайный рецепт
        recipe = random.choice(recipes)
        
        # Парсим детали рецепта
        recipe_details = await parse_recipe_page(recipe['url'])
        
        if not recipe_details:
            return None
        
        return {
            'title': recipe['title'],
            'url': recipe['url'],
            'image': recipe.get('image'),
            'ingredients': recipe_details.get('ingredients', 'Ингредиенты не указаны'),
            'instructions': recipe_details.get('instructions', 'Инструкция не указана'),
            'prep_time': recipe_details.get('prep_time', 'Время не указано'),
            'cook_time': recipe_details.get('cook_time', 'Время не указано'),
            'servings': recipe_details.get('servings', 'Количество порций не указано')
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка при получении рецепта: {e}")
        return None


async def get_recipe_list() -> List[Dict[str, str]]:
    """
    Получает список всех рецептов с главной страницы.
    """
    # Проверяем кэш
    import time
    if _recipe_cache['recipes'] and _recipe_cache['last_update']:
        if time.time() - _recipe_cache['last_update'] < _recipe_cache['cache_duration']:
            logger.debug("📦 Использую кэшированный список рецептов")
            return _recipe_cache['recipes']
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(RECIPES_URL, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }) as response:
                if response.status != 200:
                    logger.error(f"❌ Ошибка доступа к сайту: {response.status}")
                    return []
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                recipes = []
                
                # Ищем статьи с рецептами
                articles = soup.find_all('article')
                
                for article in articles:
                    # Находим заголовок и ссылку
                    title_elem = article.find('h2')
                    if not title_elem:
                        continue
                    
                    link = title_elem.find('a')
                    if not link:
                        continue
                    
                    title = link.text.strip()
                    url = link.get('href')
                    
                    # Полный URL
                    if url.startswith('/'):
                        url = BASE_URL + url
                    elif not url.startswith('http'):
                        url = BASE_URL + '/' + url
                    
                    # Находим изображение
                    img_elem = article.find('img')
                    image = None
                    if img_elem:
                        image = img_elem.get('src')
                        if image and image.startswith('/'):
                            image = BASE_URL + image
                    
                    recipes.append({
                        'title': title,
                        'url': url,
                        'image': image
                    })
                
                # Обновляем кэш
                _recipe_cache['recipes'] = recipes
                _recipe_cache['last_update'] = time.time()
                
                logger.info(f"📚 Найдено {len(recipes)} рецептов")
                return recipes
                
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге списка рецептов: {e}")
        return []


async def parse_recipe_page(url: str) -> Optional[Dict[str, str]]:
    """
    Парсит страницу рецепта.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }) as response:
                if response.status != 200:
                    logger.error(f"❌ Ошибка доступа к странице рецепта: {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Ищем ингредиенты
                ingredients = None
                ingredients_section = soup.find('div', class_='ingredients')
                if ingredients_section:
                    # Пытаемся найти список
                    ul = ingredients_section.find('ul')
                    if ul:
                        items = ul.find_all('li')
                        ingredients = '\n'.join([item.text.strip() for item in items])
                    else:
                        ingredients = ingredients_section.text.strip()
                
                # Ищем инструкцию
                instructions = None
                instructions_section = soup.find('div', class_='instructions')
                if instructions_section:
                    ol = instructions_section.find('ol')
                    if ol:
                        items = ol.find_all('li')
                        instructions = '\n'.join([f"{i+1}. {item.text.strip()}" for i, item in enumerate(items)])
                    else:
                        # Ищем параграфы
                        paragraphs = instructions_section.find_all('p')
                        if paragraphs:
                            instructions = '\n'.join([p.text.strip() for p in paragraphs])
                        else:
                            instructions = instructions_section.text.strip()
                
                # Ищем время приготовления
                prep_time = None
                cook_time = None
                servings = None
                
                time_elem = soup.find('span', class_='prep-time')
                if time_elem:
                    prep_time = time_elem.text.strip()
                
                cook_elem = soup.find('span', class_='cook-time')
                if cook_elem:
                    cook_time = cook_elem.text.strip()
                
                servings_elem = soup.find('span', class_='servings')
                if servings_elem:
                    servings = servings_elem.text.strip()
                
                # Если не нашли структурированно, пытаемся найти в тексте
                if not ingredients or not instructions:
                    content = soup.find('div', class_='content')
                    if content:
                        # Пытаемся найти секции
                        sections = content.find_all(['h3', 'h4'])
                        for section in sections:
                            header = section.text.lower()
                            if 'ингредиент' in header or 'состав' in header:
                                next_elem = section.find_next_sibling()
                                if next_elem:
                                    if next_elem.name == 'ul':
                                        items = next_elem.find_all('li')
                                        ingredients = '\n'.join([item.text.strip() for item in items])
                                    else:
                                        ingredients = next_elem.text.strip()
                            elif 'приготовл' in header or 'способ' in header:
                                next_elem = section.find_next_sibling()
                                if next_elem:
                                    if next_elem.name == 'ol':
                                        items = next_elem.find_all('li')
                                        instructions = '\n'.join([f"{i+1}. {item.text.strip()}" for i, item in enumerate(items)])
                                    else:
                                        instructions = next_elem.text.strip()
                
                # Если всё ещё не нашли — ищем в тексте
                if not ingredients:
                    all_text = soup.get_text()
                    lines = all_text.split('\n')
                    
                    # Ищем секцию с ингредиентами
                    for i, line in enumerate(lines):
                        if 'ингредиент' in line.lower() or 'состав' in line.lower():
                            ingredients = '\n'.join(lines[i+1:i+10])
                            break
                
                if not instructions:
                    all_text = soup.get_text()
                    lines = all_text.split('\n')
                    
                    # Ищем секцию с инструкцией
                    for i, line in enumerate(lines):
                        if 'приготовл' in line.lower() or 'способ' in line.lower():
                            instructions = '\n'.join(lines[i+1:i+15])
                            break
                
                return {
                    'ingredients': ingredients or 'Ингредиенты не найдены',
                    'instructions': instructions or 'Инструкция не найдена',
                    'prep_time': prep_time or 'Не указано',
                    'cook_time': cook_time or 'Не указано',
                    'servings': servings or 'Не указано'
                }
                
    except Exception as e:
        logger.error(f"❌ Ошибка при парсинге страницы рецепта: {e}")
        return None


async def get_daily_recipe() -> Optional[str]:
    """
    Получает рецепт дня.
    Возвращает форматированное сообщение.
    """
    recipe = await get_random_recipe()
    
    if not recipe:
        return None
    
    # Форматируем сообщение
    message = [
        f"*{recipe['title']}*",
        "",
        "📝 *Ингредиенты:*",
        recipe['ingredients'],
        "",
        "👩‍🍳 *Приготовление:*",
        recipe['instructions']
    ]
    
    # Добавляем дополнительную информацию
    if recipe.get('prep_time') and recipe['prep_time'] != 'Не указано':
        message.insert(1, f"⏰ Подготовка: {recipe['prep_time']}")
    
    if recipe.get('cook_time') and recipe['cook_time'] != 'Не указано':
        message.insert(2, f"🔥 Готовка: {recipe['cook_time']}")
    
    if recipe.get('servings') and recipe['servings'] != 'Не указано':
        message.insert(3, f"🍽️ Порции: {recipe['servings']}")
    
    # Добавляем ссылку на оригинал
    if recipe.get('url'):
        message.append("")
        message.append(f"📎 Полный рецепт: {recipe['url']}")
    
    return '\n'.join(message)


def format_recipe_for_chat(recipe: Dict[str, str]) -> str:
    """
    Форматирует рецепт для отправки в чат.
    """
    if not recipe:
        return "🧁 *Ой!* Не удалось найти рецепт сегодня :("
    
    message = (
        f"🧁 *Рецепт от Пинки Пай!*\n\n"
        f"*{recipe['title']}*\n\n"
        f"📝 *Ингредиенты:*\n{recipe['ingredients']}\n\n"
        f"👩‍🍳 *Приготовление:*\n{recipe['instructions']}"
    )
    
    # Добавляем время и порции
    extras = []
    if recipe.get('prep_time') and recipe['prep_time'] != 'Не указано':
        extras.append(f"⏰ Подготовка: {recipe['prep_time']}")
    if recipe.get('cook_time') and recipe['cook_time'] != 'Не указано':
        extras.append(f"🔥 Готовка: {recipe['cook_time']}")
    if recipe.get('servings') and recipe['servings'] != 'Не указано':
        extras.append(f"🍽️ Порции: {recipe['servings']}")
    
    if extras:
        message += "\n\n" + "\n".join(extras)
    
    # Добавляем ссылку
    if recipe.get('url'):
        message += f"\n\n📎 Подробнее: {recipe['url']}"
    
    return message
