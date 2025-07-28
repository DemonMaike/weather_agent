import pytest
from unittest.mock import MagicMock
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


@pytest.fixture(autouse=True)
def mock_os_chdir(monkeypatch):
    """
    Мокает os.chdir, чтобы предотвратить изменение текущей рабочей директории
    во время выполнения тестов, если это делает gradio_app.py.
    """
    with monkeypatch.context() as m:
        m.setattr(os, 'chdir', MagicMock())
        yield


@pytest.fixture(autouse=True)
def mock_event_loop_and_executor(monkeypatch):
    mock_loop = MagicMock()
    mock_loop.is_closed.return_value = False
    mock_loop.run_forever.return_value = None
    mock_loop.stop.return_value = None
    mock_loop.call_soon_threadsafe.return_value = None

    mock_executor = MagicMock()
    mock_executor.shutdown.return_value = None

    def mock_get_event_loop():
        return mock_loop

    monkeypatch.setattr('src.ui.gradio_app.get_event_loop', mock_get_event_loop)
    monkeypatch.setattr('src.ui.gradio_app._loop', mock_loop)
    monkeypatch.setattr('src.ui.gradio_app._executor', mock_executor)

    monkeypatch.setattr('asyncio.run_coroutine_threadsafe',
                        MagicMock(return_value=MagicMock(result=lambda timeout: "mocked async result")))
    monkeypatch.setattr('src.ui.gradio_app.run_async', MagicMock(return_value="mocked run_async result"))

    yield


@pytest.fixture(autouse=True)
def mock_agent_initialization(monkeypatch):
    mock_agent = MagicMock()
    mock_agent.chat.return_value = "Mocked chat response"
    mock_agent.get_available_tools.return_value = ["geo", "weather"]
    mock_agent.clear_memory.return_value = None
    mock_agent.cleanup_mcp.return_value = None

    monkeypatch.setattr('src.agent.react_agent.create_modern_weather_agent', MagicMock(return_value=mock_agent))

    mock_modern_langchain_react_agent_class = MagicMock()
    mock_modern_langchain_react_agent_class.return_value = mock_agent
    monkeypatch.setattr('src.agent.react_agent.ModernLangChainReActAgent', mock_modern_langchain_react_agent_class)

    mock_ui_instance = MagicMock()
    mock_ui_instance.is_initialized = False
    mock_ui_instance.agent = None
    mock_ui_instance.sessions = {"default": "mock_session_id"}
    mock_ui_instance.current_session = "default"
    mock_ui_instance.chat_history = {"default": []}
    mock_ui_instance.initialize_agent.return_value = ("✅ Агент успешно инициализирован!", "Mock session info")
    mock_ui_instance.chat_with_agent.return_value = ("", [("user", "agent")])
    mock_ui_instance._get_session_info.return_value = "Mock session info"
    mock_ui_instance.create_new_session.return_value = ("status", [], "session_info")
    mock_ui_instance.switch_session.return_value = ("status", [], "session_info")
    mock_ui_instance.clear_current_session.return_value = ([], "status")
    mock_ui_instance.delete_session.return_value = ("status", "session_info")
    mock_ui_instance.get_sessions_list.return_value = ["default", "session2"]
    mock_ui_instance.get_available_tools.return_value = "Mocked tools info"
    mock_ui_instance.export_session_history.return_value = "Mocked export status"

    monkeypatch.setattr('src.ui.gradio_app.ui_instance', mock_ui_instance)
    yield


def test_gradio_interface_creation():
    """
    Проверяет, что Gradio интерфейс создается без ошибок.
    """
    from src.ui.gradio_app import create_gradio_interface

    try:
        demo = create_gradio_interface()
        assert demo is not None, "Gradio Blocks должен быть создан"
        print("✅ Gradio интерфейс успешно создан.")
    except Exception as e:
        pytest.fail(f"Ошибка при создании Gradio интерфейса: {e}")
