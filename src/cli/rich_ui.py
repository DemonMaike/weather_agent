"""
Простой и красивый CLI интерфейс для Weather Agent с использованием Rich
Живая консоль с красивым форматированием
"""
import asyncio
import sys
import os
from typing import Optional, List

# Добавляем корневую папку Weather Agent в sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
from rich import box
from rich.rule import Rule
import threading
import time

from src.agent.react_agent import create_react_agent


class WeatherAgentRichUI:
    """Красивый Rich-based интерфейс для Weather Agent"""
    
    def __init__(self):
        self.console = Console()
        self.agent = None
        self.is_agent_ready = False
        self.chat_history = []
        
    def create_header(self) -> Panel:
        """Создание заголовка приложения"""
        title = Text("🌤️ Weather Agent - ReAct AI с MCP интеграцией", style="bold cyan")
        subtitle = Text("Современный CLI интерфейс для работы с погодными данными", style="dim")
        
        header_content = Align.center(
            Text.assemble(title, "\n", subtitle),
            vertical="middle"
        )
        
        return Panel(
            header_content,
            box=box.ROUNDED,
            style="blue",
            height=5
        )
    
    def create_status_panel(self, status: str, mcp_status: str = "") -> Panel:
        """Создание панели статуса"""
        content = Text()
        content.append("📊 Статус: ", style="bold")
        content.append(status, style="green" if "готов" in status.lower() else "yellow")
        
        if mcp_status:
            content.append("\n🔗 MCP: ", style="bold")
            content.append(mcp_status, style="green" if "подключен" in mcp_status.lower() else "red")
        
        return Panel(
            content,
            title="Состояние системы",
            box=box.ROUNDED,
            style="cyan"
        )
    
    def create_chat_panel(self) -> Panel:
        """Создание панели чата"""
        if not self.chat_history:
            content = Text("Добро пожаловать! Задайте вопрос о погоде...", style="dim italic")
        else:
            content = Text()
            for entry in self.chat_history[-10:]:  # Показываем последние 10 сообщений
                if entry['type'] == 'user':
                    content.append("👤 Вы: ", style="bold blue")
                    content.append(f"{entry['message']}\n\n", style="white")
                elif entry['type'] == 'agent':
                    content.append("🤖 Agent: ", style="bold green")
                    content.append(f"{entry['message']}", style="white")
                    if entry.get('tools_used'):
                        content.append(f"\n🔧 Инструменты: {', '.join(entry['tools_used'])}", style="dim cyan")
                    content.append("\n\n")
                elif entry['type'] == 'system':
                    content.append("ℹ️ Система: ", style="bold yellow")
                    content.append(f"{entry['message']}\n\n", style="yellow")
        
        return Panel(
            content,
            title="💬 Чат с агентом",
            box=box.ROUNDED,
            style="white",
            height=20
        )
    
    def create_help_panel(self) -> Panel:
        """Создание панели помощи"""
        help_text = """
🌤️ **Команды Weather Agent:**

• Просто введите вопрос о погоде
• `help` - показать эту справку
• `clear` - очистить чат
• `quit` или `exit` - выйти

**Примеры запросов:**
• Какая погода в Москве?
• Сравни погоду в Лондоне и Париже
• Прогноз на завтра для Санкт-Петербурга
"""
        
        return Panel(
            Markdown(help_text),
            title="📖 Справка",
            box=box.ROUNDED,
            style="magenta"
        )
    
    def add_message(self, message: str, msg_type: str, tools_used: List[str] = None):
        """Добавить сообщение в историю чата"""
        entry = {
            'type': msg_type,
            'message': message,
            'timestamp': time.time()
        }
        if tools_used:
            entry['tools_used'] = tools_used
        
        self.chat_history.append(entry)
    
    async def initialize_agent(self) -> bool:
        """Инициализация ReAct агента"""
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("🔄 Инициализация ReAct агента...", total=None)
                
                # Подавляем вывод во время инициализации
                original_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w') if os.name != 'nt' else open('nul', 'w')
                
                try:
                    self.agent = await create_react_agent()
                    self.is_agent_ready = True
                    
                    # Проверяем MCP инструменты
                    if hasattr(self.agent, 'tools') and self.agent.tools:
                        tools_list = list(self.agent.tools.keys())
                        mcp_status = f"✅ Подключен: {', '.join(tools_list)}"
                    else:
                        mcp_status = "⚠️ Не подключен"
                    
                finally:
                    sys.stdout.close()
                    sys.stdout = original_stdout
                
                progress.update(task, completed=True)
            
            self.add_message("✅ ReAct агент инициализирован и готов к работе!", "system")
            return True
            
        except Exception as e:
            self.add_message(f"❌ Ошибка инициализации: {str(e)}", "system")
            return False
    
    async def process_user_input(self, user_input: str) -> str:
        """Обработка пользовательского ввода"""
        if not self.is_agent_ready:
            return "❌ Агент еще не готов. Подождите инициализации."
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True
            ) as progress:
                task = progress.add_task("🤔 Анализирую запрос...", total=None)
                
                # Подавляем вывод агента
                original_stdout = sys.stdout
                sys.stdout = open(os.devnull, 'w') if os.name != 'nt' else open('nul', 'w')
                
                try:
                    # Отслеживаем использованные инструменты
                    tools_used = []
                    if hasattr(self.agent, '_execute_action'):
                        original_execute = self.agent._execute_action
                        
                        def tracked_execute(action: str, action_input: str) -> str:
                            if action not in tools_used:
                                tools_used.append(action)
                            return original_execute(action, action_input)
                        
                        self.agent._execute_action = tracked_execute
                    
                    # Выполняем запрос
                    response = self.agent.chat(user_input)
                    
                    # Восстанавливаем оригинальный метод
                    if hasattr(self.agent, '_execute_action'):
                        self.agent._execute_action = original_execute
                    
                finally:
                    sys.stdout.close()
                    sys.stdout = original_stdout
                
                progress.update(task, completed=True)
            
            # Добавляем сообщения в историю
            self.add_message(user_input, "user")
            self.add_message(response, "agent", tools_used)
            
            return response
            
        except Exception as e:
            error_msg = f"❌ Ошибка: {str(e)}"
            self.add_message(error_msg, "system")
            return error_msg
    
    def show_help(self):
        """Показать справку"""
        self.console.print(self.create_help_panel())
        self.console.print()
    
    def clear_chat(self):
        """Очистить чат"""
        self.chat_history.clear()
        self.add_message("🧹 Чат очищен", "system")
    
    async def run(self):
        """Основной цикл приложения"""
        self.console.clear()
        
        # Показываем заголовок
        self.console.print(self.create_header())
        self.console.print()
        
        # Инициализируем агент
        await self.initialize_agent()
        
        # Главный цикл
        while True:
            try:
                # Показываем статус
                status = "✅ Готов к работе" if self.is_agent_ready else "❌ Не готов"
                mcp_status = "✅ MCP подключен" if self.is_agent_ready else "❌ MCP не подключен"
                
                self.console.print(self.create_status_panel(status, mcp_status))
                self.console.print()
                
                # Показываем чат
                self.console.print(self.create_chat_panel())
                self.console.print()
                
                # Запрашиваем ввод пользователя
                self.console.print(Panel(
                    "Введите ваш вопрос о погоде (или 'help', 'clear', 'quit'):",
                    style="bold cyan"
                ))
                
                user_input = Prompt.ask("🌤️", console=self.console).strip()
                
                if not user_input:
                    continue
                
                # Обрабатываем команды
                if user_input.lower() in ['quit', 'exit', 'q']:
                    if Confirm.ask("Вы уверены, что хотите выйти?", console=self.console):
                        break
                elif user_input.lower() in ['help', 'помощь', 'h']:
                    self.show_help()
                    continue
                elif user_input.lower() in ['clear', 'очистить', 'c']:
                    self.clear_chat()
                    self.console.clear()
                    self.console.print(self.create_header())
                    continue
                
                # Обрабатываем запрос к агенту
                await self.process_user_input(user_input)
                
                # Очищаем экран для следующей итерации
                self.console.print("\n" + "="*80 + "\n")
                
            except KeyboardInterrupt:
                if Confirm.ask("\nВы хотите выйти?", console=self.console):
                    break
            except Exception as e:
                self.console.print(f"[red]Ошибка: {e}[/red]")
        
        self.console.print(Panel(
            Align.center("👋 До свидания! Weather Agent завершает работу."),
            style="green"
        ))


async def run_weather_rich_ui():
    """Запуск Rich UI приложения"""
    ui = WeatherAgentRichUI()
    await ui.run()


if __name__ == "__main__":
    try:
        asyncio.run(run_weather_rich_ui())
    except KeyboardInterrupt:
        print("\nРабота завершена")
    except Exception as e:
        print(f"Ошибка запуска: {e}")