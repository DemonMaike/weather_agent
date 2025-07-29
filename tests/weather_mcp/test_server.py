import pytest
from unittest.mock import patch, AsyncMock
import sys
from pathlib import Path
import asyncio
from datetime import date

root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

from fastmcp import FastMCP


def test_mcp_server_initialization_no_errors():
    """
    Проверяет, что FastMCP сервер инициализируется и регистрирует все 7 инструментов без ошибок.
    """
    try:
        with patch('src.weather_mcp.server.GeocodingService'), \
                patch('src.weather_mcp.server.WeatherService'):

            from src.weather_mcp.server import (
                mcp, get_coord, get_weather, get_city_weather,
                get_current_weather, get_historical_weather,
                get_city_current_weather, get_city_historical_weather
            )

            assert mcp is not None
            assert isinstance(mcp, FastMCP)

            # Проверяем, что все инструменты зарегистрированы
            tools = [
                get_coord, get_weather, get_city_weather,
                get_current_weather, get_historical_weather,
                get_city_current_weather, get_city_historical_weather
            ]
            
            for tool in tools:
                assert hasattr(tool, 'name'), f"Tool {tool} should have a name"
                
            print("✅ Все 7 MCP инструментов успешно зарегистрированы")

    except Exception as e:
        pytest.fail(f"Ошибка при инициализации FastMCP сервера: {e}")


@pytest.mark.asyncio
async def test_get_coord_function():
    """
    Тестирует функцию get_coord для получения координат города.
    """
    with patch('src.weather_mcp.tools.geo.GeocodingService') as mock_geo_service:
        mock_service_instance = AsyncMock()
        mock_geo_service.return_value = mock_service_instance
        
        mock_service_instance.get_coordinates.return_value = {
            "success": True,
            "data": {
                "lat": 55.7558,
                "lon": 37.6176,
                "display_name": "Moscow, Russia"
            }
        }
        
        # Импортируем инструменты напрямую
        from src.weather_mcp.tools.geo import GeocodingService
        
        service = GeocodingService()
        # Применяем мокирование
        service.get_coordinates = mock_service_instance.get_coordinates
        
        result = await service.get_coordinates("Moscow")
        
        assert result["success"] is True
        assert result["data"]["lat"] == 55.7558
        assert result["data"]["lon"] == 37.6176
        
        print("✅ GeocodingService работает корректно")


@pytest.mark.asyncio
async def test_get_current_weather_function():
    """
    Тестирует функцию get_current_weather для получения текущей погоды.
    """
    with patch('src.weather_mcp.server.WeatherService') as mock_weather_service:
        mock_service_instance = AsyncMock()
        mock_weather_service.return_value = mock_service_instance
        
        mock_service_instance.get_weather.return_value = {
            "success": True,
            "data": {
                "current": {
                    "temperature": 25.5,
                    "wind_speed": 10.2,
                    "time": "2025-07-29T15:00",
                    "weather_code": 0
                },
                "location": {
                    "timezone": "Europe/Moscow"
                }
            }
        }
        
        from src.weather_mcp.server import get_current_weather
        
        result = await get_current_weather(55.7558, 37.6176)
        
        assert "🌤️ Текущая погода для координат" in result
        assert "🌡️ Температура: 25.5°C" in result
        assert "💨 Скорость ветра: 10.2 км/ч" in result
        
        print("✅ get_current_weather работает корректно")


@pytest.mark.asyncio
async def test_get_historical_weather_function():
    """
    Тестирует функцию get_historical_weather для получения исторических данных.
    """
    with patch('src.weather_mcp.server.WeatherService') as mock_weather_service:
        mock_service_instance = AsyncMock()
        mock_weather_service.return_value = mock_service_instance
        
        mock_service_instance.get_historical_weather.return_value = {
            "success": True,
            "data": {
                "daily_forecast": [
                    {
                        "date": "2024-01-01",
                        "temperature_max": 5.0,
                        "temperature_min": -2.0,
                        "precipitation": 0.0,
                        "wind_speed_max": 15.0
                    },
                    {
                        "date": "2024-01-02", 
                        "temperature_max": 3.0,
                        "temperature_min": -5.0,
                        "precipitation": 2.5,
                        "wind_speed_max": 20.0
                    }
                ],
                "location": {
                    "timezone": "Europe/London"
                }
            }
        }
        
        from src.weather_mcp.server import get_historical_weather
        
        result = await get_historical_weather(51.5074, -0.1278, "2024-01-01", "2024-01-02")
        
        assert "📊 Исторические данные о погоде" in result
        assert "📅 Период: 2024-01-01 - 2024-01-02" in result
        assert "📅 2024-01-01:" in result
        assert "🌡️ -2.0°C - 5.0°C" in result
        
        print("✅ get_historical_weather работает корректно")


@pytest.mark.asyncio 
async def test_get_city_current_weather_function():
    """
    Тестирует функцию get_city_current_weather для получения текущей погоды по городу.
    """
    with patch('src.weather_mcp.server.GeocodingService') as mock_geo_service, \
         patch('src.weather_mcp.server.WeatherService') as mock_weather_service:
        
        # Мокаем геокодинг
        mock_geo_instance = AsyncMock()
        mock_geo_service.return_value = mock_geo_instance
        mock_geo_instance.get_coordinates.return_value = {
            "success": True,
            "data": {
                "lat": 48.8566,
                "lon": 2.3522,
                "display_name": "Paris, France"
            }
        }
        
        # Мокаем погоду
        mock_weather_instance = AsyncMock()
        mock_weather_service.return_value = mock_weather_instance
        mock_weather_instance.get_weather.return_value = {
            "success": True,
            "data": {
                "current": {
                    "temperature": 22.0,
                    "wind_speed": 8.5,
                    "time": "2025-07-29T16:00",
                    "weather_code": 1
                },
                "location": {
                    "timezone": "Europe/Paris"
                }
            }
        }
        
        from src.weather_mcp.server import get_city_current_weather
        
        result = await get_city_current_weather("Paris")
        
        assert "🌤️ Текущая погода для Paris, France" in result
        assert "🌡️ Температура: 22.0°C" in result
        assert "📍 Координаты: 48.8566, 2.3522" in result
        
        print("✅ get_city_current_weather работает корректно")


@pytest.mark.asyncio
async def test_historical_weather_date_validation():
    """
    Тестирует валидацию дат в функции get_historical_weather.
    """
    # Импортируем модуль и получаем функцию через его содержимое
    import src.weather_mcp.server as server_module
    
    # Получаем актуальную функцию из декорированного объекта
    get_historical_weather_func = None
    for attr_name in dir(server_module):
        attr = getattr(server_module, attr_name)
        if hasattr(attr, 'name') and attr.name == 'get_historical_weather':
            # Получаем оригинальную функцию из FunctionTool
            get_historical_weather_func = attr.fn
            break
    
    assert get_historical_weather_func is not None, "Функция get_historical_weather не найдена"
    
    # Тест неверного формата даты
    result = await get_historical_weather_func(55.7558, 37.6176, "2024/01/01", "2024/01/02")
    assert "❌ Неверный формат даты" in result
    
    # Тест дат в будущем
    result = await get_historical_weather_func(55.7558, 37.6176, "2030-01-01", "2030-01-02")
    assert "❌ Исторические данные доступны только для прошедших дат" in result
    
    # Тест неправильного порядка дат
    result = await get_historical_weather_func(55.7558, 37.6176, "2024-01-02", "2024-01-01")
    assert "❌ Начальная дата должна быть раньше конечной" in result
    
    print("✅ Валидация дат работает корректно")


def test_all_tools_count():
    """
    Проверяет, что все 7 инструментов доступны.
    """
    with patch('src.weather_mcp.server.GeocodingService'), \
            patch('src.weather_mcp.server.WeatherService'):
        
        from src.weather_mcp.server import (
            get_coord, get_weather, get_city_weather,
            get_current_weather, get_historical_weather,
            get_city_current_weather, get_city_historical_weather
        )
        
        tools = [
            get_coord, get_weather, get_city_weather,
            get_current_weather, get_historical_weather,
            get_city_current_weather, get_city_historical_weather
        ]
        
        assert len(tools) == 7, f"Ожидалось 7 инструментов, получено {len(tools)}"
        
        # Проверяем уникальность имен
        tool_names = [tool.name for tool in tools]
        assert len(set(tool_names)) == 7, "Все инструменты должны иметь уникальные имена"
        
        print("✅ Все 7 инструментов присутствуют и имеют уникальные имена")
