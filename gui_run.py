#!/usr/bin/env python3
"""
Простой скрипт для запуска Gradio UI
"""
import sys
import os

# Добавляем корневую папку проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.ui.gradio_app import main

if __name__ == "__main__":
    print("🌤️ Запуск Weather Agent UI...")
    print("=" * 50)
    print("🔗 Интерфейс будет доступен по адресу: http://localhost:7860")
    print("✨ Агент автоматически инициализируется при первом сообщении")
    print("🔧 Используемые инструменты будут показаны в начале ответов")
    print("=" * 50)
    main()