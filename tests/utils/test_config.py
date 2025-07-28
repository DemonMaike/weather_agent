from src.utils.config import Settings

def test_settings_non_empty_variables():
    settings = Settings()

    # Проверяем, что GOOGLE_API_KEY не пустой
    assert settings.GOOGLE_API_KEY is not None
    assert settings.GOOGLE_API_KEY != ""

    # Проверяем, что LLM_MODEL не пустой
    assert settings.LLM_MODEL is not None
    assert settings.LLM_MODEL != ""