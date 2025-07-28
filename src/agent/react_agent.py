"""
Современный ReAct агент с правильной интеграцией MCP через MultiServerMCPClient
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any

# Современные импорты
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver

# Современная MCP интеграция
from langchain_mcp_adapters.client import MultiServerMCPClient

# Исправление кодировки для Windows
if sys.platform == "win32":
    import codecs

    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stdin.reconfigure(encoding='utf-8')
    except AttributeError:
        try:
            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
            sys.stdin = codecs.getreader("utf-8")(sys.stdin.detach())
        except:
            pass

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from src.utils.config import settings
except ImportError:
    class Settings:
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


    settings = Settings()


class ModernLangChainReActAgent:
    """
    Современный ReAct агент с MultiServerMCPClient
    """

    def __init__(self, api_key: Optional[str] = None, max_iterations: int = 20,
                 server_path: str = "weather_mcp/server.py"):
        # Инициализируем атрибуты
        self.server_path = server_path
        self.max_iterations = max_iterations
        self.agent = None
        self.tools: List = []
        self.initialized = False
        self.mcp_client: Optional[MultiServerMCPClient] = None

        # Память для агента
        self.memory = InMemorySaver()

        # Проверяем API ключ
        self.api_key = api_key or getattr(settings, 'GOOGLE_API_KEY', None)
        if not self.api_key:
            raise ValueError(
                "Google Gemini API ключ не найден!\n"
                "Получите его на https://aistudio.google.com/app/apikey\n"
                "и установите переменную GOOGLE_API_KEY"
            )

        # Создаем модель Google Gemini
        try:
            self.model = ChatGoogleGenerativeAI(
                model=settings.LLM_MODEL,
                google_api_key=self.api_key,
                temperature=0.1,
                max_tokens=2048
            )
            print("✅ Google Gemini модель создана успешно")
        except Exception as e:
            raise ValueError(f"Ошибка создания модели Gemini: {e}")

        print("✅ ReAct агент инициализирован")

    def _resolve_server_path(self, server_path: str) -> Path:
        """Умный поиск пути к MCP серверу"""
        current_dir = Path(__file__).parent

        possible_paths = [
            current_dir / server_path,
            current_dir / "weather_mcp" / "server.py",
            current_dir.parent / "weather_mcp" / "server.py",
            current_dir.parent.parent / "weather_mcp" / "server.py",
            current_dir.parent / "mcp_weather_server.py",
            current_dir.parent.parent / "mcp_weather_server.py",
            Path(server_path).resolve()
        ]

        for path in possible_paths:
            if path.exists():
                print(f"🎯 Найден MCP сервер: {path}")
                return path

        print(f"⚠️ MCP сервер не найден, используем: {server_path}")
        return Path(server_path).resolve()

    async def initialize_mcp(self) -> bool:
        """Современная инициализация MCP с MultiServerMCPClient"""
        if self.initialized:
            print("ℹ️ MCP уже инициализирован, пропускаем")
            return True

        try:
            server_path_abs = self._resolve_server_path(self.server_path)
            print(f"🚀 Подключение к MCP серверу через MultiServerMCPClient: {server_path_abs}")

            # Создаем современный MCP клиент
            self.mcp_client = MultiServerMCPClient({
                "weather": {
                    "command": sys.executable,
                    "args": [str(server_path_abs)],
                    "transport": "stdio"
                }
            })

            print("🔧 Загрузка MCP инструментов...")

            # Загружаем инструменты - это все что нужно!
            self.tools = await self.mcp_client.get_tools()
            print(f"✅ Загружено {len(self.tools)} MCP инструментов: {[t.name for t in self.tools]}")

            # Создаем ReAct агент
            print("🤖 Создание ReAct агента...")
            self.agent = create_react_agent(
                model=self.model,
                tools=self.tools,
                checkpointer=self.memory,
                state_modifier=(
                    "Ты умный ассистент для работы с погодными данными. "
                    "Используй доступные инструменты для ответа на вопросы пользователя. "
                    "Всегда вызывай инструмент get_weather для любых вопросов о погоде. "
                    "Если пользователь спрашивает прогноз на несколько дней, используй параметр count_days. "
                    "ВАЖНО: Всегда отвечай на русском языке! "
                    "Будь дружелюбным и подробно объясняй информацию о погоде."
                )
            )

            self.initialized = True
            print("🎉 ReAct агент готов к работе!")
            return True

        except Exception as e:
            print(f"❌ Ошибка инициализации MCP: {e}")
            await self.cleanup_mcp()
            return False

    async def chat(self, user_input: str, thread_id: Optional[str] = None) -> str:
        """Отправка сообщения агенту"""
        if not self.initialized:
            print("🔄 Инициализация MCP...")
            success = await self.initialize_mcp()
            if not success:
                return "❌ Ошибка: не удалось подключиться к MCP серверу."

        try:
            if thread_id is None:
                thread_id = str(uuid.uuid4())

            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": self.max_iterations
            }

            print(f"💭 Обработка: {user_input[:50]}{'...' if len(user_input) > 50 else ''}")

            # Используем агент с уже загруженными инструментами
            response = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )

            if response and "messages" in response:
                last_message = response["messages"][-1]
                if isinstance(last_message, AIMessage):
                    return last_message.content
                elif hasattr(last_message, 'content'):
                    return str(last_message.content)

            return "❌ Не удалось получить ответ от агента"

        except Exception as e:
            print(f"🐛 DEBUG: Ошибка в chat: {e}")
            return f"❌ Произошла ошибка: {str(e)}"

    async def get_conversation_history(self, thread_id: str) -> List[Dict[str, Any]]:
        """Получение истории разговора"""
        try:
            config = {"configurable": {"thread_id": thread_id}}

            # Используем метод графа для получения состояния
            state = await self.agent.aget_state(config)

            if state and hasattr(state, 'values') and "messages" in state.values:
                history = []
                for msg in state.values["messages"]:
                    history.append({
                        "type": type(msg).__name__,
                        "content": msg.content[:200] + "..." if len(str(msg.content)) > 200 else msg.content,
                        "timestamp": getattr(msg, 'additional_kwargs', {}).get('timestamp', None)
                    })
                return history
            else:
                return [{"info": f"История для потока {thread_id[:8]}... пуста"}]

        except Exception as e:
            print(f"🐛 Ошибка получения истории: {e}")
            return [{"error": f"Ошибка: {str(e)}"}]

    async def clear_memory(self, thread_id: str) -> bool:
        """Очистка памяти для конкретного потока"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            await self.memory.adelete_state(config)
            print(f"🧹 Память потока {thread_id[:8]}... очищена")
            return True
        except Exception as e:
            print(f"🐛 Ошибка очистки памяти: {e}")
            return False

    async def get_available_tools(self) -> List[str]:
        """Получение списка доступных MCP инструментов"""
        if not self.initialized:
            await self.initialize_mcp()

        return [tool.name for tool in self.tools] if self.tools else []

    async def cleanup_mcp(self):
        """Правильная очистка MCP ресурсов"""
        try:
            # MultiServerMCPClient автоматически управляет соединениями
            if hasattr(self, 'mcp_client') and self.mcp_client:
                # Если есть метод close, используем его
                if hasattr(self.mcp_client, 'close'):
                    await self.mcp_client.close()
                self.mcp_client = None
                print("🧹 MCP клиент очищен")

            if hasattr(self, 'initialized'):
                self.initialized = False
            if hasattr(self, 'tools'):
                self.tools = []
            if hasattr(self, 'agent'):
                self.agent = None

            print("✅ Все MCP ресурсы очищены")

        except Exception as e:
            print(f"🐛 Ошибка при очистке MCP: {e}")
            # Принудительно очищаем все ссылки
            self.mcp_client = None
            self.initialized = False

    def __del__(self):
        """Безопасный деструктор"""
        try:
            if hasattr(self, 'initialized') and getattr(self, 'initialized', False):
                self.initialized = False
        except:
            pass

    async def __aenter__(self):
        """Context manager entry"""
        if not self.initialized:
            await self.initialize_mcp()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - очищаем ресурсы"""
        await self.cleanup_mcp()


async def create_modern_weather_agent(
        api_key: Optional[str] = None,
        with_mcp: bool = True,
        server_path: str = "weather_mcp/server.py",
        max_iterations: int = 20
) -> ModernLangChainReActAgent:
    """Фабричная функция для создания современного агента"""
    agent = ModernLangChainReActAgent(
        api_key=api_key,
        max_iterations=max_iterations,
        server_path=server_path
    )

    if with_mcp:
        await agent.initialize_mcp()

    return agent


async def main():
    """Основная функция"""
    print("🌤️ Запуск Modern ReAct Weather Agent...")
    print("=" * 60)

    try:
        print("🔧 Создание современного агента...")
        agent = await create_modern_weather_agent()

        if not agent.initialized:
            print("❌ Не удалось инициализировать агент")
            return

        session_id = str(uuid.uuid4())
        tools_list = await agent.get_available_tools()

        print("\n🎉 Modern ReAct Weather Agent готов к работе!")
        print(f"🔧 Доступные инструменты: {tools_list}")
        print(f"🆔 Session ID: {session_id[:8]}...")
        print("\n📝 Команды:")
        print("  • 'exit', 'quit', 'выход' - завершить работу")
        print("  • 'clear', 'очистить' - очистить историю диалога")
        print("  • 'new', 'новый' - начать новую сессию")
        print("  • 'history', 'история' - показать историю диалога")
        print("  • 'tools', 'инструменты' - показать доступные инструменты")
        print("=" * 60)
        print("\n🗣️ Начинаем интерактивный чат...")

        # Основной цикл взаимодействия
        while True:
            try:
                user_input = input("\n🧑 Вы: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['exit', 'quit', 'выход', 'q']:
                    print("👋 До свидания!")
                    break

                elif user_input.lower() in ['clear', 'очистить', 'c']:
                    success = await agent.clear_memory(session_id)
                    if success:
                        print("✅ История диалога очищена")
                    continue

                elif user_input.lower() in ['new', 'новый', 'n']:
                    session_id = str(uuid.uuid4())
                    print(f"🆕 Начата новая сессия: {session_id[:8]}...")
                    continue

                elif user_input.lower() in ['history', 'история', 'h']:
                    history = await agent.get_conversation_history(session_id)
                    if history and len(history) > 0:
                        print("📜 История диалога:")
                        for i, msg in enumerate(history[-5:], 1):
                            msg_type = msg.get('type', 'Unknown')
                            content = str(msg.get('content', ''))
                            if len(content) > 100:
                                content = content[:100] + "..."
                            print(f"  {i}. {msg_type}: {content}")
                    else:
                        print("📜 История диалога пуста")
                    continue

                elif user_input.lower() in ['tools', 'инструменты', 't']:
                    tools = await agent.get_available_tools()
                    if tools:
                        print(f"🔧 Доступные инструменты: {', '.join(tools)}")
                    else:
                        print("🔧 Нет доступных инструментов")
                    continue

                # Обычное сообщение агенту
                print("🤖 Агент обрабатывает запрос...")
                response = await agent.chat(user_input, thread_id=session_id)
                print(f"\n🤖 Агент: {response}")

            except KeyboardInterrupt:
                print("\n\n👋 Принудительное завершение (Ctrl+C)")
                break

            except EOFError:
                print("\n\n👋 Завершение по EOF")
                break

            except UnicodeDecodeError as e:
                print(f"❌ Ошибка кодировки: {e}")
                print("💡 Попробуйте запустить: chcp 65001 (Windows)")
                continue

            except Exception as e:
                print(f"❌ Неожиданная ошибка: {e}")
                print("🔄 Продолжаем работу...")
                continue

        # Очищаем ресурсы при завершении
        print("\n🧹 Очистка ресурсов...")
        await agent.cleanup_mcp()
        print("✅ Программа завершена")

    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")

    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        print("🔧 Проверьте:")
        print("  1. GOOGLE_API_KEY установлен")
        print("  2. MCP сервер доступен")
        print("  3. Все зависимости установлены")


if __name__ == "__main__":
    asyncio.run(main())
