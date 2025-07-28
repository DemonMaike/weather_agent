import sys
import logging
from pathlib import Path
from fastmcp import FastMCP

root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path / 'src'))

from weather_mcp.tools.geo import GeocodingService
from weather_mcp.tools.weater import WeatherService

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

mcp = FastMCP("weather-agent")


@mcp.tool()
async def get_weather(city: str, count_days: int = 1) -> str:
    """Получить прогноз погоды для указанного города

    Args:
        city: Название города
        count_days: Количество дней для прогноза (1-7)
    """
    if not 1 <= count_days <= 7:
        return "Количество дней должно быть от 1 до 7"

    try:
        geo = GeocodingService()
        geo_result = await geo.get_coordinates(city)

        if not geo_result.get("success"):
            error_msg = geo_result.get("error", "Неизвестная ошибка геокодирования")
            logging.error(f"Geocoding error: {error_msg}")
            return f"Ошибка при поиске города: {error_msg}"

        geo_data = geo_result.get("data")
        if not geo_data:
            return f"Не удалось получить данные для города '{city}'"

        lat = geo_data.get("lat")
        lon = geo_data.get("lon")
        city_display_name = geo_data.get("display_name", city)

        if not lat or not lon:
            return f"Некорректные координаты для города '{city}'"

        weather = WeatherService()
        weather_result = await weather.get_weather(lat, lon, count_days)

        if not weather_result.get("success"):
            error_msg = weather_result.get("error", "Неизвестная ошибка получения погоды")
            logging.error(f"Weather error: {error_msg}")
            return f"Ошибка при получении погоды: {error_msg}"

        weather_data = weather_result.get("data")
        if not weather_data:
            return f"Не удалось получить данные о погоде для города '{city}'"

        response_text = f"🌤️ Прогноз погоды для {city_display_name}\n\n"

        if "current" in weather_data:
            current = weather_data["current"]
            response_text += f"📍 Текущая погода:\n"
            response_text += f"🌡️ Температура: {current.get('temperature', 'N/A')}°C\n"
            response_text += f"💨 Скорость ветра: {current.get('wind_speed', 'N/A')} км/ч\n"
            response_text += f"📅 Время: {current.get('time', 'N/A')}\n\n"

        if "daily_forecast" in weather_data and weather_data["daily_forecast"]:
            response_text += f"📈 Прогноз на {len(weather_data['daily_forecast'])} дн.:\n"
            for day in weather_data['daily_forecast']:
                date_str = day.get('date', 'N/A')
                temp_max = day.get('temperature_max', 'N/A')
                temp_min = day.get('temperature_min', 'N/A')
                precipitation = day.get('precipitation', 'N/A')
                wind_max = day.get('wind_speed_max', 'N/A')

                response_text += f"📅 {date_str}:\n"
                response_text += f"  🌡️ {temp_min}°C - {temp_max}°C\n"
                response_text += f"  🌧️ Осадки: {precipitation} мм\n"
                response_text += f"  💨 Макс. ветер: {wind_max} км/ч\n\n"

        if "location" in weather_data:
            location = weather_data["location"]
            response_text += f"📍 Координаты: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}\n"
            response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_weather: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении погоды: {str(e)}"


if __name__ == "__main__":
    mcp.run()
