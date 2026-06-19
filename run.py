#!/usr/bin/env python3
# run.py
"""
Точка входа для запуска бота Пинки Пай.
Запускает основное приложение с обработкой ошибок.

Автор: MADAO81
"""

import sys
import logging
from bot.main import main

if __name__ == "__main__":
    try:
        print("🦄 Запуск бота Пинки Пай...")
        print("📝 Автор: MADAO81")
        print("📋 Версия: 1.0.0")
        print("-" * 40)
        main()
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logging.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)
