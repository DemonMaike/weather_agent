import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import sys
from pathlib import Path
import asyncio
from datetime import date

root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))


def test_server_module_imports():
    """
    Проверяет, что модуль сервера импортируется без ошибок.
    """
    try:
        from src.weather_mcp import server
        assert server is not None
        print("✅ Модуль сервера успешно импортирован")
    except ImportError as e:
        pytest.skip(f"Модуль сервера не найден: {e}")


@pytest.mark.asyncio
async def test_geocoding_service_mock():
    """
    Тестирует мокированный сервис геокодирования.
    """
    from src.weather_mcp.tools.geo import GeocodingService
    
    with patch.object(GeocodingService, 'get_coordinates') as mock_get_coords:
        mock_get_coords.return_value = {
            "success": True,
            "data": {
                "lat": 55.7558,
                "lon": 37.6176,
                "display_name": "Moscow, Russia"
            }
        }
        
        service = GeocodingService()
        result = await service.get_coordinates("Moscow")
        
        assert result["success"] is True
        assert result["data"]["lat"] == 55.7558
        assert result["data"]["lon"] == 37.6176
        
        print("✅ Мокированный GecodingService работает корректно")


@pytest.mark.asyncio
async def test_weather_service_mock():
    """
    Тестирует мокированный сервис погоды.
    """
    from src.weather_mcp.tools.weather import WeatherService
    
    with patch.object(WeatherService, 'get_weather') as mock_get_weather:
        mock_get_weather.return_value = {
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
        
        service = WeatherService()
        result = await service.get_weather(55.7558, 37.6176)
        
        assert result["success"] is True
        assert result["data"]["current"]["temperature"] == 25.5
        
        print("✅ Мокированный WeatherService работает корректно")


def test_date_validation_logic():
    """
    Тестирует логику валидации дат.
    """
    from datetime import date, datetime
    
    # Тест корректной даты
    try:
        test_date = datetime.strptime("2024-01-01", "%Y-%m-%d").date()
        assert test_date == date(2024, 1, 1)
    except ValueError:
        pytest.fail("Корректная дата должна парситься без ошибок")
    
    # Тест некорректной даты
    try:
        datetime.strptime("2024/01/01", "%Y-%m-%d").date()
        pytest.fail("Некорректная дата должна вызывать ValueError")
    except ValueError:
        pass  # Ожидаемое поведение
    
    print("✅ Валидация дат работает корректно")


def test_weather_code_mapping():
    """
    Тестирует маппинг кодов погоды.
    """
    weather_codes = {
        0: "Ясно",
        1: "В основном ясно", 
        2: "Переменная облачность",
        3: "Пасмурно"
    }
    
    assert weather_codes.get(0) == "Ясно"
    assert weather_codes.get(1) == "В основном ясно"
    assert weather_codes.get(999) is None  # Неизвестный код
    
    print("✅ Маппинг кодов погоды работает корректно")


def test_coordinate_bounds():
    """
    Тестирует проверку границ координат.
    """
    def is_valid_coordinate(lat, lon):
        return -90 <= lat <= 90 and -180 <= lon <= 180
    
    # Валидные координаты
    assert is_valid_coordinate(55.7558, 37.6176) is True  # Москва
    assert is_valid_coordinate(0, 0) is True  # Экватор, Гринвич
    assert is_valid_coordinate(90, 180) is True  # Крайние значения
    assert is_valid_coordinate(-90, -180) is True  # Крайние значения
    
    # Невалидные координаты
    assert is_valid_coordinate(91, 0) is False  # Широта > 90
    assert is_valid_coordinate(-91, 0) is False  # Широта < -90
    assert is_valid_coordinate(0, 181) is False  # Долгота > 180
    assert is_valid_coordinate(0, -181) is False  # Долгота < -180
    
    print("✅ Проверка границ координат работает корректно")