from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

root_path = Path(__file__).parent.parent.parent
env_path = root_path / '.env'

print(root_path)
print(env_path)

class Settings(BaseSettings):
    """Класс настроек приложения.
    
    Загружает настройки из переменных окружения или .env файла,
    с значениями по умолчанию.
    
    Attributes:
        nominatim_base_url: Базовый URL для Nominatim API.
        openmeteo_base_url: Базовый URL для Open-Meteo API.
        openmeteo_archive_url: URL для Open-Meteo Archive API.
        server_host: Хост сервера.
        server_port: Порт сервера.
        GEMINI_API: API ключ для Gemini.
    """

    model_config = SettingsConfigDict(env_file=env_path)
    
    # API настройки
    nominatim_base_url: str = "https://nominatim.openstreetmap.org"
    openmeteo_base_url: str = "https://api.open-meteo.com/v1"
    openmeteo_archive_url: str = "https://archive-api.open-meteo.com/v1"

    # Сервер настройки
    server_host: str = "0.0.0.0"
    server_port: int = 8000

    # LLM настройки
    GOOGLE_API_KEY: Optional[str] = None
    LLM_MODEL: Optional[str] = None


settings = Settings()

if __name__ == "__main__":
    print(settings.model_dump())