"""
Gradio интерфейс для взаимодействия с Weather Agent
"""
import asyncio
import threading
import gradio as gr
import uuid
import os
import sys
import json
from datetime import datetime
from typing import List, Tuple, Optional, Dict, Any
import concurrent.futures

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

# Меняем рабочую директорию на корень проекта для правильного поиска MCP сервера
os.chdir(project_root)
print(f"🗂️ Рабочая директория: {os.getcwd()}")
print(f"🗂️ Корень проекта: {project_root}")

from src.agent.react_agent import ModernLangChainReActAgent, create_modern_weather_agent

# Глобальный event loop для всего приложения
_loop = None
_executor = None

def get_event_loop():
    """Получает или создает глобальный event loop"""
    global _loop, _executor
    if _loop is None or _loop.is_closed():
        # Создаем новый event loop в отдельном потоке
        def run_loop():
            global _loop
            _loop = asyncio.new_event_loop()
            asyncio.set_event_loop(_loop)
            _loop.run_forever()
        
        loop_thread = threading.Thread(target=run_loop, daemon=True)
        loop_thread.start()
        
        # Ждем пока loop будет создан
        import time
        while _loop is None:
            time.sleep(0.01)
            
        _executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    
    return _loop

def run_async(coro):
    """Запускает корутину в глобальном event loop"""
    loop = get_event_loop()
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=30)  # 30 секунд таймаут


class WeatherAgentUI:
    """Класс для управления Gradio интерфейсом"""
    
    def __init__(self):
        self.agent: Optional[ModernLangChainReActAgent] = None
        self.sessions: Dict[str, str] = {}  # session_name -> session_id
        self.current_session = "default"
        self.is_initialized = False
        self.chat_history: Dict[str, List[Tuple[str, str]]] = {"default": []}
        
    async def initialize_agent(self):
        """Инициализация агента"""
        if not self.is_initialized:
            try:
                print("🚀 Инициализация агента...")
                self.agent = await create_modern_weather_agent()
                self.is_initialized = True
                if "default" not in self.sessions:
                    self.sessions["default"] = str(uuid.uuid4())
                print("✅ Агент успешно инициализирован!")
                return "✅ Агент успешно инициализирован!", self._get_session_info()
            except Exception as e:
                print(f"❌ Ошибка инициализации: {e}")
                return f"❌ Ошибка инициализации агента: {str(e)}", ""
        return "ℹ️ Агент уже инициализирован", self._get_session_info()
    
    async def _extract_tool_usage(self, response: str) -> str:
        """Извлекает информацию об использованных инструментах"""
        try:
            if self.agent and self.current_session in self.sessions:
                session_id = self.sessions[self.current_session]
                
                # Получаем историю сессии для анализа последних действий
                config = {"configurable": {"thread_id": session_id}}
                state = await self.agent.agent.aget_state(config)
                
                if state and hasattr(state, 'values') and "messages" in state.values:
                    messages = state.values["messages"]
                    
                    # Ищем последние tool calls в истории
                    used_tools = []
                    for msg in reversed(messages[-5:]):  # Смотрим последние 5 сообщений
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            for tool_call in msg.tool_calls:
                                if hasattr(tool_call, 'name'):
                                    used_tools.append(tool_call.name)
                        elif hasattr(msg, 'additional_kwargs') and 'tool_calls' in msg.additional_kwargs:
                            for tool_call in msg.additional_kwargs['tool_calls']:
                                if 'function' in tool_call and 'name' in tool_call['function']:
                                    used_tools.append(tool_call['function']['name'])
                    
                    if used_tools:
                        unique_tools = list(set(used_tools))
                        return f"🔧 Использованы инструменты: {', '.join(unique_tools)}\n\n"
                
        except Exception as e:
            print(f"🐛 Ошибка извлечения инструментов: {e}")
        
        return ""
    
    def _get_session_info(self):
        """Получение информации о текущей сессии"""
        if self.current_session in self.sessions:
            session_id = self.sessions[self.current_session]
            return f"🆔 Текущая сессия: {self.current_session} ({session_id[:8]}...)"
        return "❌ Нет активной сессии"
    
    async def chat_with_agent(self, message: str, history: List[Tuple[str, str]]) -> Tuple[str, List[Tuple[str, str]]]:
        """Обработка сообщения пользователя"""
        if not self.is_initialized or not self.agent:
            print("🔄 Агент не инициализирован, инициализирую...")
            init_result, _ = await self.initialize_agent()
            if "❌" in init_result:
                return init_result, history
        
        # Обеспечиваем наличие сессии
        if self.current_session not in self.sessions:
            self.sessions[self.current_session] = str(uuid.uuid4())
            
        try:
            session_id = self.sessions[self.current_session]
            
            # Добавляем timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            print(f"💭 Отправка сообщения агенту: {message[:50]}...")
            response = await self.agent.chat(message, thread_id=session_id)
            print(f"✅ Получен ответ от агента")
            
            # Извлекаем информацию об использованных инструментах
            tools_info = await self._extract_tool_usage(response)
            
            # Сохраняем в локальную историю
            formatted_response = f"[{timestamp}] {tools_info}{response}"
            history.append((message, formatted_response))
            self.chat_history[self.current_session] = history
            
            return "", history
        except Exception as e:
            print(f"❌ Ошибка в чате: {e}")
            error_msg = f"❌ Ошибка: {str(e)}"
            history.append((message, error_msg))
            return "", history
    
    async def create_new_session(self, session_name: str):
        """Создание новой сессии"""
        if not session_name.strip():
            return "❌ Введите название сессии", [], self._get_session_info()
        
        session_name = session_name.strip()
        if session_name in self.sessions:
            return f"❌ Сессия '{session_name}' уже существует", [], self._get_session_info()
        
        self.sessions[session_name] = str(uuid.uuid4())
        self.current_session = session_name
        self.chat_history[session_name] = []
        
        return f"✅ Создана новая сессия: {session_name}", [], self._get_session_info()
    
    async def switch_session(self, session_name: str):
        """Переключение между сессиями"""
        if session_name not in self.sessions:
            return f"❌ Сессия '{session_name}' не найдена", [], self._get_session_info()
        
        self.current_session = session_name
        history = self.chat_history.get(session_name, [])
        
        return f"✅ Переключено на сессию: {session_name}", history, self._get_session_info()
    
    async def clear_current_session(self):
        """Очистка текущей сессии"""
        if self.agent and self.current_session in self.sessions:
            session_id = self.sessions[self.current_session]
            await self.agent.clear_memory(session_id)
        
        self.chat_history[self.current_session] = []
        return [], f"🧹 Сессия '{self.current_session}' очищена"
    
    async def delete_session(self, session_name: str):
        """Удаление сессии"""
        if session_name == "default":
            return "❌ Нельзя удалить сессию по умолчанию", self._get_session_info()
        
        if session_name not in self.sessions:
            return f"❌ Сессия '{session_name}' не найдена", self._get_session_info()
        
        # Очищаем память агента
        if self.agent:
            session_id = self.sessions[session_name]
            await self.agent.clear_memory(session_id)
        
        # Удаляем сессию
        del self.sessions[session_name]
        if session_name in self.chat_history:
            del self.chat_history[session_name]
        
        # Переключаемся на default если удаляли текущую
        if self.current_session == session_name:
            self.current_session = "default"
            if "default" not in self.sessions:
                self.sessions["default"] = str(uuid.uuid4())
                self.chat_history["default"] = []
        
        return f"✅ Сессия '{session_name}' удалена", self._get_session_info()
    
    def get_sessions_list(self):
        """Получение списка сессий"""
        return list(self.sessions.keys())
    
    async def get_available_tools(self):
        """Получение списка доступных инструментов"""
        if not self.is_initialized or not self.agent:
            await self.initialize_agent()
        
        if self.agent:
            tools = await self.agent.get_available_tools()
            return f"🔧 Доступные инструменты: {', '.join(tools)}" if tools else "❌ Нет доступных инструментов"
        return "❌ Агент не инициализирован"
    
    async def export_session_history(self, session_name: str):
        """Экспорт истории сессии в JSON"""
        if session_name not in self.chat_history:
            return "❌ Сессия не найдена"
        
        history = self.chat_history[session_name]
        export_data = {
            "session_name": session_name,
            "session_id": self.sessions.get(session_name, "unknown"),
            "export_time": datetime.now().isoformat(),
            "messages_count": len(history),
            "history": [{"user": msg[0], "agent": msg[1]} for msg in history]
        }
        
        filename = f"chat_history_{session_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return f"✅ История экспортирована в файл: {filename}"
        except Exception as e:
            return f"❌ Ошибка экспорта: {str(e)}"


# Создаем глобальный экземпляр UI
ui_instance = WeatherAgentUI()


def sync_chat_wrapper(message, history):
    """Синхронная обертка для чата"""
    return run_async(ui_instance.chat_with_agent(message, history))


def sync_clear_wrapper():
    """Синхронная обертка для очистки истории"""
    history, status = run_async(ui_instance.clear_current_session())
    return history, status


def sync_new_session_wrapper(session_name):
    """Синхронная обертка для создания новой сессии"""
    status, history, session_info = run_async(ui_instance.create_new_session(session_name))
    return status, history, session_info, gr.Dropdown(choices=ui_instance.get_sessions_list(), value=ui_instance.current_session)


def sync_switch_session_wrapper(session_name):
    """Синхронная обертка для переключения сессии"""
    status, history, session_info = run_async(ui_instance.switch_session(session_name))
    return status, history, session_info


def sync_delete_session_wrapper(session_name):
    """Синхронная обертка для удаления сессии"""
    status, session_info = run_async(ui_instance.delete_session(session_name))
    current_history = ui_instance.chat_history.get(ui_instance.current_session, [])
    return status, session_info, current_history, gr.Dropdown(choices=ui_instance.get_sessions_list(), value=ui_instance.current_session)


def sync_export_wrapper(session_name):
    """Синхронная обертка для экспорта истории"""
    return run_async(ui_instance.export_session_history(session_name))


def create_gradio_interface():
    """Создание Gradio интерфейса"""
    
    with gr.Blocks(
        title="🌤️ Weather Agent",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .chat-container {
            height: 600px;
        }
        .session-panel {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
        """
    ) as demo:
        
        gr.Markdown("""
        # 🌤️ Weather Agent - Умный помощник по погоде
        
        Интеллектуальный помощник с поддержкой множественных сессий чата.
        Агент автоматически использует нужные инструменты и показывает их в ответах.
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                # Основной чат
                chatbot = gr.Chatbot(
                    label="💬 Чат с агентом",
                    elem_classes=["chat-container"],
                    show_label=True,
                    avatar_images=(None, "🤖")
                )
                
                msg = gr.Textbox(
                    label="Ваше сообщение",
                    placeholder="Например: Какая погода в Москве?",
                    lines=2,
                    max_lines=5
                )
                
                with gr.Row():
                    send_btn = gr.Button("📤 Отправить", variant="primary")
                    clear_btn = gr.Button("🧹 Очистить чат", variant="secondary")
            
            with gr.Column(scale=1):
                # Панель управления сессиями
                with gr.Group(elem_classes=["session-panel"]):
                    gr.Markdown("### 📂 Управление сессиями")
                    
                    session_info = gr.Textbox(
                        label="Текущая сессия",
                        value="default",
                        interactive=False
                    )
                    
                    # Создание новой сессии
                    new_session_name = gr.Textbox(
                        label="Название новой сессии",
                        placeholder="Введите название"
                    )
                    create_session_btn = gr.Button("➕ Создать сессию")
                    
                    # Переключение сессий
                    session_dropdown = gr.Dropdown(
                        label="Выберите сессию",
                        choices=["default"],
                        value="default"
                    )
                    switch_btn = gr.Button("🔄 Переключить")
                    delete_btn = gr.Button("🗑️ Удалить сессию", variant="stop")
                    
                    # Экспорт истории
                    export_btn = gr.Button("💾 Экспорт истории")
                    
                    session_status = gr.Textbox(
                        label="Статус операции",
                        value="",
                        interactive=False
                    )
                
                # Примеры запросов
                gr.Markdown("""
                ### 📝 Примеры запросов:
                - "Какая погода в Москве?"
                - "Прогноз на завтра для СПб"
                - "Погода в Лондоне на 5 дней"
                - "Температура в Токио сейчас"
                - "Сравни погоду в Москве и Киеве"
                
                ### 🔧 Инструменты
                Агент автоматически использует:
                - Геокодирование городов
                - Получение текущей погоды
                - Прогноз погоды на несколько дней
                """)
        
        # Обработчики событий
        def handle_send(message, history):
            if not message.strip():
                return "", history
            return sync_chat_wrapper(message, history)
        
        def handle_clear():
            history, status = sync_clear_wrapper()
            return history, status
        
        # Привязка основных событий
        send_btn.click(
            handle_send,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        msg.submit(
            handle_send,
            inputs=[msg, chatbot],
            outputs=[msg, chatbot]
        )
        
        clear_btn.click(
            handle_clear,
            outputs=[chatbot, session_status]
        )
        
        # Привязка событий сессий
        create_session_btn.click(
            sync_new_session_wrapper,
            inputs=[new_session_name],
            outputs=[session_status, chatbot, session_info, session_dropdown]
        )
        
        switch_btn.click(
            sync_switch_session_wrapper,
            inputs=[session_dropdown],
            outputs=[session_status, chatbot, session_info]
        )
        
        delete_btn.click(
            sync_delete_session_wrapper,
            inputs=[session_dropdown],
            outputs=[session_status, session_info, chatbot, session_dropdown]
        )
        
        export_btn.click(
            sync_export_wrapper,
            inputs=[session_dropdown],
            outputs=[session_status]
        )
        
        # Очистка полей после создания сессии
        create_session_btn.click(
            lambda: "",
            outputs=[new_session_name]
        )
    
    return demo


def cleanup_resources():
    """Очистка ресурсов при завершении"""
    global _loop, _executor, ui_instance
    
    try:
        if ui_instance and ui_instance.agent:
            # Запускаем очистку агента в event loop
            if _loop and not _loop.is_closed():
                future = asyncio.run_coroutine_threadsafe(ui_instance.agent.cleanup_mcp(), _loop)
                future.result(timeout=5)
        
        if _executor:
            _executor.shutdown(wait=True)
            
        if _loop and not _loop.is_closed():
            _loop.call_soon_threadsafe(_loop.stop)
            
        print("✅ Ресурсы очищены")
    except Exception as e:
        print(f"⚠️ Ошибка при очистке ресурсов: {e}")


def main():
    """Главная функция запуска Gradio интерфейса"""
    print("🚀 Запуск Gradio интерфейса для Weather Agent...")
    
    try:
        # Создаем интерфейс
        demo = create_gradio_interface()
        
        # Запускаем сервер
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True,
            show_error=True,
            inbrowser=True
        )
    except KeyboardInterrupt:
        print("\n👋 Завершение работы...")
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
    finally:
        cleanup_resources()


if __name__ == "__main__":
    import atexit
    atexit.register(cleanup_resources)
    main()