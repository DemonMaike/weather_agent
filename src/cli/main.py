"""
Красивый CLI интерфейс для Weather Agent
Элегантный консольный интерфейс с индикаторами прогресса
"""
import asyncio
import sys
import os
import time
import threading
from typing import Optional, List, Dict, Any

# Добавляем корневую папку Weather Agent в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agent.react_agent import create_react_agent


class LoadingSpinner:
    """Красивый спиннер для отображения прогресса"""
    
    def __init__(self, message: str = "Думаю"):
        self.message = message
        self.is_running = False
        self.thread = None
        self.spinner_chars = ["|", "/", "-", "\\"]
        
    def start(self):
        """Запуск спиннера"""
        self.is_running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        
    def stop(self):
        """Остановка спиннера"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        # Очищаем строку
        print("\r" + " " * (len(self.message) + 10) + "\r", end="", flush=True)
        
    def _spin(self):
        """Анимация спиннера"""
        i = 0
        while self.is_running:
            char = self.spinner_chars[i % len(self.spinner_chars)]
            print(f"\r{char} {self.message}...", end="", flush=True)
            time.sleep(0.1)
            i += 1


class QuietReActAgent:
    """Тихий ReAct агент без отладочного вывода"""
    
    def __init__(self):
        self.agent = None
        self.mcp_tools_used = []
        
    async def initialize(self):
        """Инициализация агента"""
        # Перехватываем весь вывод
        self._redirect_output()
        
        try:
            self.agent = await create_react_agent()
            return True
        except Exception as e:
            self._restore_output()
            print(f"\nОшибка инициализации: {e}")
            return False
        finally:
            self._restore_output()
    
    def _redirect_output(self):
        """Перенаправляем stdout для подавления отладочного вывода"""
        self.original_stdout = sys.stdout
        if os.name == 'nt':  # Windows
            sys.stdout = open('nul', 'w')
        else:  # Unix/Linux/Mac
            sys.stdout = open(os.devnull, 'w')
        
    def _restore_output(self):
        """Восстанавливаем stdout"""
        if hasattr(self, 'original_stdout'):
            sys.stdout.close()
            sys.stdout = self.original_stdout
    
    def chat(self, message: str) -> tuple[str, List[str]]:
        """
        Общение с агентом с отслеживанием используемых инструментов
        
        Returns:
            tuple: (ответ_агента, список_использованных_инструментов)
        """
        if not self.agent:
            return "Агент не инициализирован", []
            
        # Перехватываем вывод
        self._redirect_output()
        
        try:
            # Очищаем список использованных инструментов
            self.mcp_tools_used = []
            
            # Модифицируем агент для отслеживания инструментов
            original_execute = self.agent._execute_action
            
            def tracked_execute(action: str, action_input: str) -> str:
                if action not in self.mcp_tools_used:
                    self.mcp_tools_used.append(action)
                return original_execute(action, action_input)
            
            self.agent._execute_action = tracked_execute
            
            # Выполняем запрос
            response = self.agent.chat(message)
            
            # Восстанавливаем оригинальный метод
            self.agent._execute_action = original_execute
            
            return response, self.mcp_tools_used
            
        except Exception as e:
            return f"Произошла ошибка: {str(e)}", []
        finally:
            self._restore_output()
    
    def stop(self):
        """Остановка агента"""
        if self.agent:
            self.agent.stop_mcp_server()


class WeatherAgentCLI:
    """Главный CLI интерфейс"""
    
    def __init__(self):
        self.agent = QuietReActAgent()
        
    def print_header(self):
        """Печать красивого заголовка"""
        header = """
+==============================================================+
|                     Weather Agent                           |
|                  ReAct AI с MCP интеграцией                  |
+==============================================================+
        """
        print(header)
        
    def print_help(self):
        """Печать справки"""
        help_text = """
Команды:
  - Просто введите ваш вопрос о погоде
  - 'help' или 'помощь' - показать справку
  - 'exit', 'quit', 'выход' - завершить работу
  
Примеры:
  - Какая погода в Москве?
  - Сравни погоду в Москве и Питере
  - Какая погода будет завтра в Лондоне?
        """
        print(help_text)
        
    async def initialize(self):
        """Инициализация CLI"""
        spinner = LoadingSpinner("Инициализация Weather Agent")
        spinner.start()
        
        try:
            success = await self.agent.initialize()
            spinner.stop()
            
            if success:
                print("+ Weather Agent готов к работе!")
                return True
            else:
                print("- Не удалось инициализировать агент")
                return False
                
        except Exception as e:
            spinner.stop()
            print(f"- Ошибка инициализации: {e}")
            return False
    
    def format_tools_info(self, tools: List[str]) -> str:
        """Форматирование информации об используемых инструментах"""
        if not tools:
            return ""
            
        if len(tools) == 1:
            return f"[MCP] Использован инструмент: {tools[0]}"
        else:
            tools_str = ", ".join(tools)
            return f"[MCP] Использованы инструменты: {tools_str}"
    
    async def run(self):
        """Главный цикл интерфейса"""
        self.print_header()
        
        # Инициализация
        if not await self.initialize():
            return
            
        print("\nВведите ваш вопрос о погоде (или 'help' для справки):")
        
        try:
            while True:
                # Ввод пользователя
                print("\n" + "-" * 60)
                user_input = input("\nВопрос: ").strip()
                
                if not user_input:
                    continue
                    
                # Обработка команд
                if user_input.lower() in ['exit', 'quit', 'выход', 'q']:
                    print("\nДо свидания!")
                    break
                    
                if user_input.lower() in ['help', 'помощь', 'h']:
                    self.print_help()
                    continue
                
                # Обработка запроса
                print()
                spinner = LoadingSpinner("Анализирую запрос")
                spinner.start()
                
                try:
                    # Выполняем запрос
                    response, tools_used = self.agent.chat(user_input)
                    spinner.stop()
                    
                    # Показываем информацию об инструментах
                    tools_info = self.format_tools_info(tools_used)
                    if tools_info:
                        print(f"\n{tools_info}")
                    
                    # Показываем ответ
                    print(f"\nОтвет:")
                    print(f"   {response}")
                    
                except Exception as e:
                    spinner.stop()
                    print(f"\nОшибка: {str(e)}")
                    
        except KeyboardInterrupt:
            print("\n\nРабота прервана пользователем")
        except Exception as e:
            print(f"\nНеожиданная ошибка: {e}")
        finally:
            # Остановка агента
            self.agent.stop()


async def main():
    """Точка входа в приложение"""
    cli = WeatherAgentCLI()
    await cli.run()


if __name__ == "__main__":
    # Запуск CLI
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nРабота завершена")
    except Exception as e:
        print(f"Критическая ошибка: {e}")