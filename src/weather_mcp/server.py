import sys
import logging
from pathlib import Path
from fastmcp import FastMCP
from datetime import date, datetime

root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path / 'src'))

from weather_mcp.tools.geo import GeocodingService
from weather_mcp.tools.weater import WeatherService

logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

mcp = FastMCP("weather-agent")


@mcp.tool()
async def get_coord(city: str) -> str:
    """Получить координаты города для дальнейшего использования

    Args:
        city: Название города
    """
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

        response_text = f"📍 Координаты для {city_display_name}:\n\n"
        response_text += f"🌍 Широта: {lat}\n"
        response_text += f"🌍 Долгота: {lon}\n"
        response_text += f"📍 Полное название: {city_display_name}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_coord: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении координат: {str(e)}"


@mcp.tool()
async def get_weather(lat: float, lon: float, count_days: int = 1) -> str:
    """Получить прогноз погоды по координатам

    Args:
        lat: Широта (например: 55.7558 для Москвы)
        lon: Долгота (например: 37.6176 для Москвы)
        count_days: Количество дней для прогноза (1-16)
    """
    if not 1 <= count_days <= 16:
        return "Количество дней должно быть от 1 до 16"

    try:
        weather = WeatherService()
        weather_result = await weather.get_weather(lat, lon, count_days)

        if not weather_result.get("success"):
            error_msg = weather_result.get("error", "Неизвестная ошибка получения погоды")
            logging.error(f"Weather error: {error_msg}")
            return f"Ошибка при получении погоды: {error_msg}"

        weather_data = weather_result.get("data")
        if not weather_data:
            return f"Не удалось получить данные о погоде для координат {lat}, {lon}"

        response_text = f"🌤️ Прогноз погоды для координат {lat}, {lon}\n\n"

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
            response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_weather: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении погоды: {str(e)}"


# @mcp.tool()
# async def get_city_weather(city: str, count_days: int = 1) -> str:
#     """Получить прогноз погоды для указанного города (удобный метод)
#
#     Args:
#         city: Название города
#         count_days: Количество дней для прогноза (1-16)
#     """
#     if not 1 <= count_days <= 16:
#         return "Количество дней должно быть от 1 до 16"
#
#     try:
#         geo = GeocodingService()
#         geo_result = await geo.get_coordinates(city)
#
#         if not geo_result.get("success"):
#             error_msg = geo_result.get("error", "Неизвестная ошибка геокодирования")
#             logging.error(f"Geocoding error: {error_msg}")
#             return f"Ошибка при поиске города: {error_msg}"
#
#         geo_data = geo_result.get("data")
#         if not geo_data:
#             return f"Не удалось получить данные для города '{city}'"
#
#         lat = geo_data.get("lat")
#         lon = geo_data.get("lon")
#         city_display_name = geo_data.get("display_name", city)
#
#         if not lat or not lon:
#             return f"Некорректные координаты для города '{city}'"
#
#         weather = WeatherService()
#         weather_result = await weather.get_weather(lat, lon, count_days)
#
#         if not weather_result.get("success"):
#             error_msg = weather_result.get("error", "Неизвестная ошибка получения погоды")
#             logging.error(f"Weather error: {error_msg}")
#             return f"Ошибка при получении погоды: {error_msg}"
#
#         weather_data = weather_result.get("data")
#         if not weather_data:
#             return f"Не удалось получить данные о погоде для города '{city}'"
#
#         response_text = f"🌤️ Прогноз погоды для {city_display_name}\n\n"
#
#         if "current" in weather_data:
#             current = weather_data["current"]
#             response_text += f"📍 Текущая погода:\n"
#             response_text += f"🌡️ Температура: {current.get('temperature', 'N/A')}°C\n"
#             response_text += f"💨 Скорость ветра: {current.get('wind_speed', 'N/A')} км/ч\n"
#             response_text += f"📅 Время: {current.get('time', 'N/A')}\n\n"
#
#         if "daily_forecast" in weather_data and weather_data["daily_forecast"]:
#             response_text += f"📈 Прогноз на {len(weather_data['daily_forecast'])} дн.:\n"
#             for day in weather_data['daily_forecast']:
#                 date_str = day.get('date', 'N/A')
#                 temp_max = day.get('temperature_max', 'N/A')
#                 temp_min = day.get('temperature_min', 'N/A')
#                 precipitation = day.get('precipitation', 'N/A')
#                 wind_max = day.get('wind_speed_max', 'N/A')
#
#                 response_text += f"📅 {date_str}:\n"
#                 response_text += f"  🌡️ {temp_min}°C - {temp_max}°C\n"
#                 response_text += f"  🌧️ Осадки: {precipitation} мм\n"
#                 response_text += f"  💨 Макс. ветер: {wind_max} км/ч\n\n"
#
#         if "location" in weather_data:
#             location = weather_data["location"]
#             response_text += f"📍 Координаты: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}\n"
#             response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}"
#
#         return response_text
#
#     except Exception as e:
#         error_details = f"Ошибка в get_city_weather: {type(e).__name__}: {str(e)}"
#         logging.error(error_details)
#         return f"Произошла ошибка при получении погоды: {str(e)}"


@mcp.tool()
async def get_current_weather(lat: float, lon: float) -> str:
    """Получить только текущую погоду по координатам (без прогноза)

    Args:
        lat: Широта (например: 55.7558 для Москвы)
        lon: Долгота (например: 37.6176 для Москвы)
    """
    try:
        weather = WeatherService()
        weather_result = await weather.get_weather(lat, lon, forecast_days=1, include_current=True)

        if not weather_result.get("success"):
            error_msg = weather_result.get("error", "Неизвестная ошибка получения погоды")
            logging.error(f"Weather error: {error_msg}")
            return f"Ошибка при получении текущей погоды: {error_msg}"

        weather_data = weather_result.get("data")
        if not weather_data:
            return f"Не удалось получить данные о текущей погоде для координат {lat}, {lon}"

        response_text = f"🌤️ Текущая погода для координат {lat}, {lon}\n\n"

        if "current" in weather_data:
            current = weather_data["current"]
            response_text += f"📍 Сейчас:\n"
            response_text += f"🌡️ Температура: {current.get('temperature', 'N/A')}°C\n"
            response_text += f"💨 Скорость ветра: {current.get('wind_speed', 'N/A')} км/ч\n"
            response_text += f"📅 Время: {current.get('time', 'N/A')}\n"
            response_text += f"🔢 Код погоды: {current.get('weather_code', 'N/A')}\n\n"
        else:
            return "❌ Текущие данные о погоде недоступны"

        if "location" in weather_data:
            location = weather_data["location"]
            response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_current_weather: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении текущей погоды: {str(e)}"


@mcp.tool()  
async def get_historical_weather(lat: float, lon: float, start_date: str, end_date: str) -> str:
    """Получить исторические данные о погоде по координатам

    Args:
        lat: Широта (например: 55.7558 для Москвы)
        lon: Долгота (например: 37.6176 для Москвы)
        start_date: Начальная дата в формате YYYY-MM-DD (например: 2024-01-01)
        end_date: Конечная дата в формате YYYY-MM-DD (например: 2024-01-07)
    """
    try:
        # Парсим даты
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return "❌ Неверный формат даты. Используйте YYYY-MM-DD (например: 2024-01-01)"

        # Проверяем, что даты в прошлом
        today = date.today()
        if start_date_obj >= today or end_date_obj >= today:
            return "❌ Исторические данные доступны только для прошедших дат"

        # Проверяем порядок дат
        if start_date_obj > end_date_obj:
            return "❌ Начальная дата должна быть раньше конечной"

        # Ограничиваем период (например, максимум 1 год)
        if (end_date_obj - start_date_obj).days > 365:
            return "❌ Максимальный период для исторических данных: 365 дней"

        weather = WeatherService()
        weather_result = await weather.get_historical_weather(lat, lon, start_date_obj, end_date_obj)

        if not weather_result.get("success"):
            error_msg = weather_result.get("error", "Неизвестная ошибка получения исторических данных")
            logging.error(f"Historical weather error: {error_msg}")
            return f"Ошибка при получении исторических данных: {error_msg}"

        weather_data = weather_result.get("data")
        if not weather_data:
            return f"Не удалось получить исторические данные для координат {lat}, {lon}"

        response_text = f"📊 Исторические данные о погоде для координат {lat}, {lon}\n"
        response_text += f"📅 Период: {start_date} - {end_date}\n\n"

        if "daily_forecast" in weather_data and weather_data["daily_forecast"]:
            response_text += f"📈 Данные за {len(weather_data['daily_forecast'])} дн.:\n"
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
            response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_historical_weather: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении исторических данных: {str(e)}"


@mcp.tool()
async def get_city_current_weather(city: str) -> str:
    """Получить текущую погоду для указанного города (удобный метод)

    Args:
        city: Название города
    """
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

        # Получаем текущую погоду напрямую через WeatherService
        weather = WeatherService()
        weather_result = await weather.get_weather(lat, lon, forecast_days=1, include_current=True)

        if not weather_result.get("success"):
            error_msg = weather_result.get("error", "Неизвестная ошибка получения погоды")
            logging.error(f"Weather error: {error_msg}")
            return f"Ошибка при получении текущей погоды: {error_msg}"

        weather_data = weather_result.get("data")
        if not weather_data:
            return f"Не удалось получить данные о текущей погоде для города '{city}'"

        response_text = f"🌤️ Текущая погода для {city_display_name}\n\n"

        if "current" in weather_data:
            current = weather_data["current"]
            response_text += f"📍 Сейчас:\n"
            response_text += f"🌡️ Температура: {current.get('temperature', 'N/A')}°C\n"
            response_text += f"💨 Скорость ветра: {current.get('wind_speed', 'N/A')} км/ч\n"
            response_text += f"📅 Время: {current.get('time', 'N/A')}\n"
            response_text += f"🔢 Код погоды: {current.get('weather_code', 'N/A')}\n\n"
        else:
            return "❌ Текущие данные о погоде недоступны"

        if "location" in weather_data:
            location = weather_data["location"]
            response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}\n"
        
        response_text += f"📍 Координаты: {lat}, {lon}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_city_current_weather: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении текущей погоды: {str(e)}"


@mcp.tool()
async def get_city_historical_weather(city: str, start_date: str, end_date: str) -> str:
    """Получить исторические данные о погоде для указанного города (удобный метод)

    Args:
        city: Название города
        start_date: Начальная дата в формате YYYY-MM-DD (например: 2024-01-01)
        end_date: Конечная дата в формате YYYY-MM-DD (например: 2024-01-07)
    """
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

        # Парсим даты
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return "❌ Неверный формат даты. Используйте YYYY-MM-DD (например: 2024-01-01)"

        # Проверяем, что даты в прошлом
        today = date.today()
        if start_date_obj >= today or end_date_obj >= today:
            return "❌ Исторические данные доступны только для прошедших дат"

        # Проверяем порядок дат
        if start_date_obj > end_date_obj:
            return "❌ Начальная дата должна быть раньше конечной"

        # Ограничиваем период (например, максимум 1 год)
        if (end_date_obj - start_date_obj).days > 365:
            return "❌ Максимальный период для исторических данных: 365 дней"

        # Получаем исторические данные напрямую через WeatherService
        weather = WeatherService()
        weather_result = await weather.get_historical_weather(lat, lon, start_date_obj, end_date_obj)

        if not weather_result.get("success"):
            error_msg = weather_result.get("error", "Неизвестная ошибка получения исторических данных")
            logging.error(f"Historical weather error: {error_msg}")
            return f"Ошибка при получении исторических данных: {error_msg}"

        weather_data = weather_result.get("data")
        if not weather_data:
            return f"Не удалось получить исторические данные для города '{city}'"

        response_text = f"📊 Исторические данные о погоде для {city_display_name}\n"
        response_text += f"📅 Период: {start_date} - {end_date}\n\n"

        if "daily_forecast" in weather_data and weather_data["daily_forecast"]:
            response_text += f"📈 Данные за {len(weather_data['daily_forecast'])} дн.:\n"
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
            response_text += f"🕒 Часовой пояс: {location.get('timezone', 'N/A')}\n"
            
        response_text += f"📍 Координаты: {lat}, {lon}"

        return response_text

    except Exception as e:
        error_details = f"Ошибка в get_city_historical_weather: {type(e).__name__}: {str(e)}"
        logging.error(error_details)
        return f"Произошла ошибка при получении исторических данных: {str(e)}"


if __name__ == "__main__":
    mcp.run()
