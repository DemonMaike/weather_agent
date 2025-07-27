import pytest
import httpx
from unittest.mock import patch, MagicMock
from datetime import date

from src.mcp.tools.weater import WeatherService


@pytest.fixture
def weather_service():
    return WeatherService()


@pytest.fixture
def mock_weather_response():
    return {
        "latitude": 55.625,
        "longitude": 37.606,
        "timezone": "Europe/Moscow",
        "current_weather": {
            "temperature": 15.2,
            "windspeed": 5.1,
            "weathercode": 0,
            "time": "2024-01-01T12:00"
        },
        "daily": {
            "time": ["2024-01-01", "2024-01-02"],
            "temperature_2m_max": [18.5, 16.3],
            "temperature_2m_min": [10.2, 8.9],
            "precipitation_sum": [0.0, 2.5],
            "weather_code": [0, 61],
            "wind_speed_10m_max": [12.5, 15.8]
        }
    }


class TestWeatherService:
    
    @pytest.mark.asyncio
    async def test_get_weather_success(self, weather_service, mock_weather_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_weather_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await weather_service.get_weather(55.625, 37.606)
            
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["location"]["latitude"] == 55.625
            assert result["data"]["location"]["longitude"] == 37.606
            assert "current" in result["data"]
            assert "daily_forecast" in result["data"]
            assert len(result["data"]["daily_forecast"]) == 2

    @pytest.mark.asyncio
    async def test_get_weather_http_error(self, weather_service):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=MagicMock(), response=mock_response
        )
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await weather_service.get_weather(55.625, 37.606)
            
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_historical_weather_success(self, weather_service, mock_weather_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_weather_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            start_date = date(2024, 1, 1)
            end_date = date(2024, 1, 2)
            
            result = await weather_service.get_historical_weather(55.625, 37.606, start_date, end_date)
            
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["location"]["latitude"] == 55.625

    @pytest.mark.asyncio
    async def test_get_weather_with_parameters(self, weather_service, mock_weather_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_weather_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = mock_response
            
            result = await weather_service.get_weather(
                lat=55.625, 
                lon=37.606, 
                forecast_days=7, 
                include_current=False
            )
            
            assert result["success"] is True
            mock_instance.get.assert_called_once()
            args, kwargs = mock_instance.get.call_args
            assert kwargs["params"]["forecast_days"] == 7
            assert "current_weather" not in kwargs["params"]

    def test_format_weather_data_with_current_and_daily(self, weather_service, mock_weather_response):
        formatted = weather_service._format_weather_data(mock_weather_response)
        
        assert formatted["location"]["latitude"] == 55.625
        assert formatted["location"]["longitude"] == 37.606
        assert formatted["current"]["temperature"] == 15.2
        assert len(formatted["daily_forecast"]) == 2
        assert formatted["daily_forecast"][0]["date"] == "2024-01-01"
        assert formatted["daily_forecast"][0]["temperature_max"] == 18.5

    def test_format_weather_data_without_current(self, weather_service):
        data = {
            "latitude": 55.625,
            "longitude": 37.606,
            "timezone": "Europe/Moscow",
            "daily": {
                "time": ["2024-01-01"],
                "temperature_2m_max": [18.5],
                "temperature_2m_min": [10.2],
                "precipitation_sum": [0.0],
                "weather_code": [0],
                "wind_speed_10m_max": [12.5]
            }
        }
        
        formatted = weather_service._format_weather_data(data)
        
        assert "current" not in formatted
        assert len(formatted["daily_forecast"]) == 1