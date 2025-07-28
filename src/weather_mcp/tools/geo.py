import os
import sys
import httpx
from typing import Any

# Фикс sys.path: абсолютный путь к src/ от geo.py
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))  # tools/ → weather_mcp/ → src/
sys.path.insert(0, src_path)

from utils.config import settings  # Теперь относительно src/, без 'src.'


class GeocodingService:
    """Сервис для геокодирования через Nominatim API."""

    def __init__(self):
        self.base_url = settings.nominatim_base_url
        self.timeout = 1000  # Ограничения сервиса

    async def get_coordinates(self, city: str) -> dict[str, Any]:
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
                    timeout=self.timeout
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


# Глобальный экземпляр
geocodingservice = GeocodingService()
