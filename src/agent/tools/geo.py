import httpx
from typing import Any

from src.utils.config import settings


class GeocodingService:
    """Сервис для геокодирования через Nominatim API.
    
    Предоставляет методы для получения координат по названию города.
    """
    def __init__(self):
        """Инициализация GeocodingService с базовым URL и настройками таймаута."""
        self.base_url = settings.nominatim_base_url
        self.timeout = 1000 # Ограничения сервиса, иначе банф

    async def get_coordinates(self, city: str) -> dict[str, Any]:
        """Получить координаты города через Nominatim API.
        
        Args:
            city: Название города для поиска координат.
            
        Returns:
            Словарь, содержащий статус успеха и координаты или сообщение об ошибке.
            В случае успеха возвращает широту, долготу, полное название и имя города.
            
        Example:
            >>> service = GeocodingService()
            >>> result = await service.get_coordinates("Москва")
            >>> if result["success"]:
            ...     print(f"Lat: {result['data']['lat']}, Lon: {result['data']['lon']}")
        """
        async with httpx.AsyncClient() as client:
            params = {
                "q": city,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }

            headers = {
                "User-Agent": "my-weather-app/1.0 (i@dmitrymalyshev.ru)"
            }
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data:
                    return {
                        "success": False,
                        "error": f"Город '{city}' не найден"
                    }

                location = data[0]
                return {
                    "success": True,
                    "data": {
                        "lat": float(location["lat"]),
                        "lon": float(location["lon"]),
                        "display_name": location["display_name"],
                        "city": city
                    }
                }

            except httpx.TimeoutException:
                return {"success": False, "error": "Таймаут запроса геокодирования"}
            except Exception as e:
                return {"success": False, "error": f"Ошибка геокодирования: {str(e)}"}


# Глобальный экземпляр сервиса геокодирования
geocodingservice = GeocodingService()
