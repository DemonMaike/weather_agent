import sys
import os

# Добавляем корневую папку в sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем CLI
from src.cli.main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nРабота завершена")
    except Exception as e:
        print(f"Ошибка запуска: {e}")