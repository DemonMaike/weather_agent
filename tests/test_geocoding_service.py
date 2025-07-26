import pytest
import httpx
from unittest.mock import patch, MagicMock

from src.agent.tools.geo import GeocodingService


@pytest.fixture
def geocoding_service():
    return GeocodingService()


@pytest.fixture
def mock_geocoding_response():
    return [
        {
            "lat": "55.7558260",
            "lon": "37.6176000",
            "display_name": "Moscow, Central Federal District, Russia",
            "address": {
                "city": "Moscow",
                "country": "Russia",
                "country_code": "ru"
            }
        }
    ]


class TestGeocodingService:
    
    @pytest.mark.asyncio
    async def test_get_coordinates_success(self, geocoding_service, mock_geocoding_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_geocoding_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await geocoding_service.get_coordinates("Moscow")
            
            assert result["success"] is True
            assert "data" in result
            assert result["data"]["lat"] == 55.7558260
            assert result["data"]["lon"] == 37.6176000
            assert result["data"]["display_name"] == "Moscow, Central Federal District, Russia"
            assert result["data"]["city"] == "Moscow"

    @pytest.mark.asyncio
    async def test_get_coordinates_city_not_found(self, geocoding_service):
        mock_response = MagicMock()
        mock_response.json.return_value = []  # Empty response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await geocoding_service.get_coordinates("NonexistentCity")
            
            assert result["success"] is False
            assert "error" in result
            assert "NonexistentCity" in result["error"]

    @pytest.mark.asyncio
    async def test_get_coordinates_http_error(self, geocoding_service):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "HTTP Error", request=MagicMock(), response=mock_response
        )
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await geocoding_service.get_coordinates("Moscow")
            
            assert result["success"] is False
            assert "error" in result

    @pytest.mark.asyncio
    async def test_get_coordinates_timeout_error(self, geocoding_service):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = httpx.TimeoutException("Timeout")
            
            result = await geocoding_service.get_coordinates("Moscow")
            
            assert result["success"] is False
            assert "Таймаут" in result["error"]

    @pytest.mark.asyncio
    async def test_get_coordinates_request_parameters(self, geocoding_service, mock_geocoding_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_geocoding_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = mock_client.return_value.__aenter__.return_value
            mock_instance.get.return_value = mock_response
            
            await geocoding_service.get_coordinates("Saint Petersburg")
            
            mock_instance.get.assert_called_once()
            args, kwargs = mock_instance.get.call_args
            
            # Проверяем URL
            assert args[0] == f"{geocoding_service.base_url}/search"
            
            # Проверяем параметры
            assert kwargs["params"]["q"] == "Saint Petersburg"
            assert kwargs["params"]["format"] == "json"
            assert kwargs["params"]["limit"] == 1
            assert kwargs["params"]["addressdetails"] == 1
            
            # Проверяем заголовки
            assert "User-Agent" in kwargs["headers"]
            assert "my-weather-app/1.0" in kwargs["headers"]["User-Agent"]

    @pytest.mark.asyncio
    async def test_get_coordinates_handles_general_exception(self, geocoding_service):
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Network error")
            
            result = await geocoding_service.get_coordinates("Moscow")
            
            assert result["success"] is False
            assert "Ошибка геокодирования" in result["error"]
            assert "Network error" in result["error"]