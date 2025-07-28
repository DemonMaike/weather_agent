import sys
import httpx
from typing import Any
from datetime import date
from pathlib import Path

root_path = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_path / 'src'))

from src.utils.config import settings


class WeatherService:
    """Сервис для получения данных о погоде через Open-Meteo API.
    
    Предоставляет методы для получения текущих прогнозов погоды и
    исторических данных о погоде через Open-Meteo API.
    """
    def __init__(self):
        """Инициализация WeatherService с URL API и настройками таймаута."""
        self.forecast_base_url = settings.openmeteo_base_url
        self.archive_base_url = settings.openmeteo_archive_url
        self.timeout = 30.0

    async def get_weather(
        self,
        lat: float,
        lon: float,
        forecast_days: int = 1,
        include_current: bool = True
    ) -> dict[str, Any]:
        """Получить прогноз погоды через Open-Meteo API.
        
        Args:
            lat: Широта координаты.
            lon: Долгота координаты.
            forecast_days: Количество дней прогноза (максимум 16). По умолчанию 1.
            include_current: Включать ли текущую погоду. По умолчанию True.
            
        Returns:
            Словарь, содержащий статус успеха и данные о погоде или сообщение об ошибке.
            
        Example:
            >>> service = WeatherService()
            >>> result = await service.get_weather(55.7558, 37.6176)
            >>> if result["success"]:
            ...     print(result["data"]["current"]["temperature"])
        """

        async with httpx.AsyncClient() as client:
            params = {
                "latitude": lat,
                "longitude": lon,
                "timezone": "auto",
                "forecast_days": min(forecast_days, 16),
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "weather_code",
                    "wind_speed_10m_max"
                ]
            }

            if include_current:
                params["current_weather"] = True
                params["current"] = [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "wind_speed_10m",
                    "weather_code"
                ]

            try:
                response = await client.get(
                    f"{self.forecast_base_url}/forecast",
                    params=params,
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "success": True,
                    "data": self._format_weather_data(data)
                }

            except Exception as e:
                return {"success": False, "error": f"Ошибка прогноза погоды: {str(e)}"}

    async def get_historical_weather(
        self,
        lat: float,
        lon: float,
        start_date: date,
        end_date: date
    ) -> dict[str, Any]:
        """Получить исторические данные о погоде через Open-Meteo Archive API.
        
        Args:
            lat: Широта координаты.
            lon: Долгота координаты.
            start_date: Начальная дата для исторических данных.
            end_date: Конечная дата для исторических данных.
            
        Returns:
            Словарь, содержащий статус успеха и исторические данные о погоде или сообщение об ошибке.
            
        Example:
            >>> service = WeatherService()
            >>> start = date(2023, 1, 1)
            >>> end = date(2023, 1, 7)
            >>> result = await service.get_historical_weather(55.7558, 37.6176, start, end)
        """

        async with httpx.AsyncClient() as client:
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "timezone": "auto",
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "wind_speed_10m_max",
                    "weather_code"
                ]
            }

            try:
                response = await client.get(
                    f"{self.archive_base_url}/archive",
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()

                return {
                    "success": True,
                    "data": self._format_weather_data(data)
                }

            except Exception as e:
                return {"success": False, "error": f"Ошибка исторических данных: {str(e)}"}

    def _format_weather_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Форматирование данных о погоде из ответа API.
        
        Args:
            data: Необработанные данные о погоде из Open-Meteo API.
            
        Returns:
            Отформатированные данные о погоде с местоположением, текущей погодой и ежедневными прогнозами.
        """
        formatted = {
            "location": {
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "timezone": data.get("timezone")
            }
        }

        if "current_weather" in data:
            current = data["current_weather"]
            formatted["current"] = {
                "temperature": current.get("temperature"),
                "wind_speed": current.get("windspeed"),
                "weather_code": current.get("weathercode"),
                "time": current.get("time")
            }

        if "daily" in data:
            daily = data["daily"]
            formatted["daily_forecast"] = []

            for i in range(len(daily["time"])):
                formatted["daily_forecast"].append({
                    "date": daily["time"][i],
                    "temperature_max": daily["temperature_2m_max"][i],
                    "temperature_min": daily["temperature_2m_min"][i],
                    "precipitation": daily["precipitation_sum"][i],
                    "weather_code": daily["weather_code"][i],
                    "wind_speed_max": daily["wind_speed_10m_max"][i]
                })

        return formatted
