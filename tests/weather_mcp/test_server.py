import pytest
from unittest.mock import patch
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from fastmcp import FastMCP


def test_mcp_server_initialization_no_errors():
    """
    Проверяет, что FastMCP сервер инициализируется и регистрирует инструменты без ошибок.
    """
    try:
        with patch('src.weather_mcp.server.GeocodingService'), \
                patch('src.weather_mcp.server.WeatherService'):

            from src.weather_mcp.server import mcp, get_weather

            assert mcp is not None
            assert isinstance(mcp, FastMCP)

            assert hasattr(get_weather, 'name') and get_weather.name == 'get_weather', \
                "The 'get_weather' tool should be registered and have the correct name."


    except Exception as e:
        pytest.fail(f"Ошибка при инициализации FastMCP сервера: {e}")
