import pytest
from pathlib import Path
import os


@pytest.mark.asyncio
async def test_agent_initialization(monkeypatch):
    """
    Тестирует инициализацию агента, убеждаясь, что он использует
    моковые значения переменных окружения, а не реальные.
    """
    monkeypatch.setenv("GOOGLE_API_KEY", "test_api_key_123")
    monkeypatch.setenv("LLM_MODEL", "gemini-1.5-flash")

    from src.agent.react_agent import create_modern_weather_agent
    from src.utils.config import settings as current_settings_in_module

    print(
        f"Mocked settings (from src.utils.config.settings): GOOGLE_API_KEY={current_settings_in_module.GOOGLE_API_KEY}, LLM_MODEL={current_settings_in_module.LLM_MODEL}")

    agent = await create_modern_weather_agent(api_key="test_api_key_123", with_mcp=False)

    print(f"Loaded LLM_MODEL from agent.model: {agent.model.model}")

    assert agent is not None, "Агент должен быть создан"
    assert agent.api_key == "test_api_key_123", "GOOGLE_API_KEY должен быть задан"
    assert agent.model.model in ["gemini-1.5-flash",
                                 "models/gemini-1.5-flash"], "LLM_MODEL должен быть gemini-1.5-flash"


def test_resolve_server_path(tmp_path: Path, monkeypatch):
    """
    Тестирует разрешение пути к серверу MCP.
    """
    server_relative_path = Path("src") / "weather_mcp" / "server.py"
    mock_project_root = tmp_path
    (mock_project_root / "src" / "weather_mcp").mkdir(parents=True, exist_ok=True)
    fake_server_path = mock_project_root / server_relative_path
    fake_server_path.touch()

    from src.agent.react_agent import ModernLangChainReActAgent

    monkeypatch.setattr(os, 'getcwd', lambda: str(tmp_path))
    monkeypatch.setattr(Path, 'cwd', lambda: tmp_path)

    monkeypatch.setattr(ModernLangChainReActAgent, '_resolve_server_path', lambda self, path: fake_server_path)

    agent = ModernLangChainReActAgent(api_key="test_api_key_123")
    resolved_path = agent._resolve_server_path(
        "weather_mcp/server.py")

    assert resolved_path == fake_server_path, "Должен найти существующий путь к MCP серверу во временной директории"
    assert resolved_path.exists(), "Результирующий путь должен существовать"
