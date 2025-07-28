#!/usr/bin/env python3
"""
CLI запуска для ModernLangChainReActAgent
"""
import asyncio
import sys
import os

# Добавляем src в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Импорт основной функции
from src.agent.react_agent import main

if __name__ == "__main__":
    asyncio.run(main())