"""
Корректный ReAct агент с Google Gemini API и MCP интеграцией
Исправлены все deprecated компоненты, сохранена совместимость с существующим проектом
"""
import asyncio
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

# Современные импорты
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# MCP интеграция
from langchain_mcp_adapters.client import MultiServerMCPClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.utils.config import settings


class LangChainReActAgent:
    """
    Современный ReAct агент с исправленными deprecated компонентами
    """

    def __init__(self, api_key: Optional[str] = None, max_iterations: int = 20, server_path: str = "weather_mcp/server.py"):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        if not self.api_key:
            raise ValueError("Google Gemini API ключ не найден.")

        # Создаем модель Google Gemini (НЕ Vertex AI)
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Без префикса google-gemini/
            google_api_key=self.api_key,
            temperature=0.1,
            max_tokens=2048
        )

        self.server_path = server_path
        self.max_iterations = max_iterations

        # Современная память LangGraph вместо ConversationBufferMemory
        self.memory = MemorySaver()

        # MCP клиент и агент
        self.mcp_client = None
        self.agent = None
        self.tools = []
        self.initialized = False

        print("ReAct агент инициализирован с современными компонентами")

    def _resolve_server_path(self, server_path: str) -> Path:
        """Поиск пути к вашему MCP серверу"""
        src_root = Path(__file__).parent.parent

        # Пробуем различные возможные пути
        possible_paths = [
            src_root / "weather_mcp" / "server.py",
            src_root / server_path,
            src_root.parent / "weather_server.py",
            Path(server_path).resolve()
        ]

        for path in possible_paths:
            if path.exists():
                return path

        return Path(server_path).resolve()

    async def initialize_mcp(self):
        """Инициализация MCP с современным подходом"""
        if self.initialized:
            print("DEBUG: MCP уже инициализирован")
            return True

        try:
            server_path_abs = self._resolve_server_path(self.server_path)
            print(f"DEBUG: Подключение к MCP серверу: {server_path_abs}")

            # Современный MCP клиент вместо ручного управления stdio
            self.mcp_client = MultiServerMCPClient({
                "weather": {
                    "command": sys.executable,
                    "args": [str(server_path_abs)],
                    "transport": "stdio",
                }
            })

            # Получаем инструменты
            self.tools = await self.mcp_client.get_tools()
            print(f"Загружено MCP инструментов: {len(self.tools)}")

            # Создаем современный ReAct агент
            self.agent = create_react_agent(
                model=self.model,  # Передаем объект модели
                tools=self.tools,
                checkpointer=self.memory,  # Современная память
                # Системное сообщение на русском
                state_modifier=(
                    "Ты полезный ассистент для работы с погодными данными. "
                    "Используй доступные инструменты для ответа на вопросы пользователя. "
                    "Всегда вызывай инструмент get_weather для любых вопросов о погоде, "
                    "включая текущую (count_days=0 или 1). "
                    "ВАЖНО: Всегда отвечай на русском языке!"
                )
            )

            self.initialized = True
            print("ReAct агент и executor созданы успешно")
            return True

        except Exception as e:
            print(f"Ошибка инициализации MCP: {e}")
            await self.cleanup_mcp()
            return False

    async def chat(self, user_input: str, thread_id: Optional[str] = None) -> str:
        """Чат с агентом"""
        if not self.initialized:
            success = await self.initialize_mcp()
            if not success:
                return "Ошибка: не удалось инициализировать MCP. Попробуйте позже."

        try:
            # Создаем или используем thread_id для памяти
            if thread_id is None:
                thread_id = str(uuid.uuid4())

            config = {
                "configurable": {"thread_id": thread_id},
                "recursion_limit": self.max_iterations
            }

            # Современный вызов агента
            response = await self.agent.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )

            # Извлекаем ответ
            if response and "messages" in response:
                last_message = response["messages"][-1]
                if isinstance(last_message, AIMessage):
                    return last_message.content

            return "Не удалось получить ответ"

        except Exception as e:
            print(f"DEBUG: Ошибка в chat: {e}")
            return f"Ошибка: {str(e)}"

    def get_conversation_history(self, thread_id: str):
        """Получение истории разговора для указанного потока"""
        try:
            # В LangGraph история управляется автоматически через checkpointer
            return f"История для потока {thread_id} управляется автоматически"
        except Exception as e:
            print(f"Ошибка получения истории: {e}")
            return []

    async def clear_memory(self, thread_id: str):
        """Очистка памяти для конкретного потока"""
        try:
            config = {"configurable": {"thread_id": thread_id}}
            await self.memory.adelete_state(config)
            print(f"Память потока {thread_id} очищена")
        except Exception as e:
            print(f"Ошибка очистки памяти: {e}")

    async def cleanup_mcp(self):
        """Очистка ресурсов MCP"""
        try:
            if self.mcp_client:
                # MultiServerMCPClient автоматически управляет ресурсами
                self.mcp_client = None
            self.initialized = False
            print("✅ Ресурсы MCP очищены")
        except Exception as e:
            print(f"Ошибка при очистке MCP: {e}")

    async def __aenter__(self):
        await self.initialize_mcp()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_mcp()


async def create_weather_agent(
    api_key: Optional[str] = None,
    with_mcp: bool = True,
    server_path: str = "weather_mcp/server.py",
    max_iterations: int = 20
) -> LangChainReActAgent:
    """Фабричная функция (совместимость с вашим кодом)"""
    agent = LangChainReActAgent(api_key=api_key, max_iterations=max_iterations, server_path=server_path)
    if with_mcp:
        await agent.initialize_mcp()
    return agent


if __name__ == "__main__":
    async def main():
        agent = await create_weather_agent()
        session_id = str(uuid.uuid4())  # Уникальный ID сессии

        async with agent:
            print("ReAct Weather Agent готов!")
            print(f"Доступные инструменты: {[tool.name for tool in agent.tools]}")
            print(f"Session ID: {session_id}")

            while True:
                user_input = input("Вы: ")
                if user_input.lower() in ['exit', 'quit']:
                    break
                if user_input.lower() == 'clear':
                    await agent.clear_memory(session_id)
                    continue
                if user_input.lower() == 'new':
                    session_id = str(uuid.uuid4())
                    print(f"Новая сессия: {session_id}")
                    continue
                if user_input.lower() == 'history':
                    print("История:")
                    print(agent.get_conversation_history(session_id))
                    continue

                response = await agent.chat(user_input, thread_id=session_id)
                print(f"Агент: {response}")

    asyncio.run(main())