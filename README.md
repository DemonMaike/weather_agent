# Weather Agent 🌤️

LLM-агент для получения прогноза погоды по названию города.

---

## ✅ Возможности

- 🌍 Поиск координат по названию города (геокодинг через Nominatim)
- 🌤️ Получение актуального прогноза погоды (через Open-Meteo)
- 🧠 LLM-интерфейс на базе Gemini
- 🔄 CLI и UI интерфейсы с использованием LangChain React Agent
- ⚙️ Интеграция с MCP (Model Context Protocol) для подключения к Claude Desktop и Cursor AI

---

## 🚀 Установка

```bash
git clone https://github.com/your-user/weather-agent.git
cd weather-agent
pip install -r requirements.txt
```

### 🔧 Переменные окружения

Перед запуском необходимо указать переменные окружения. Обязательная переменная:

```bash
# Обязательная переменная для запуска CLI и UI
GOOGLE_API_KEY=your_gemini_api_key
```

Вы можете указать её в `.env` или экспортировать вручную в окружение.

### 🖥️ Запуск

#### CLI

```bash
python cli_run.py
```

#### GUI

```bash
python gui_run.py
```

#### MCP конфигурация

Для удобства настройки MCP клиентов (Claude Desktop, Cursor AI) в проекте есть скрипт:

```bash
python generate_mcp_config.py
```

Он автоматически создаст корректный конфиг с учётом вашей операционной системы, путей к Python интерпретатору и серверному скрипту, а также содержит инструкцию по настройке MCP клиента.

Запустите скрипт, следуйте подсказкам — и получите готовый конфиг для подключения агента к MCP клиенту.

---

## ⚙️ Структура проекта

```
weather-agent/
├── run_cli.py               # Запуск CLI-агента
├── run_ui.py                # Запуск UI (React Agent)
├── generate_mcp_config.py   # Генератор конфигураций для MCP клиентов
├── .env                     # Файл с переменными окружения
├── requirements.txt         # Зависимости
└── src/
    └── agent/
        ├── react_agent.py   # UI-агент
        └── tools/
            ├── __init__.py
            ├── mcp.py       # MCP-интерфейс
            ├── weather.py   # Open-Meteo API
            └── geo.py       # Геокодинг через Nominatim
    └── weather_mcp/
        ├── server.py        # MCP сервер
        ├── tools/           # MCP инструменты
        └── schemas.py       # Схемы данных
    └── ui/
        ├── gradio_app.py    # Веб-интерфейс
        └── run_ui.py        # Запуск веб-интерфейса
    └── utils/
        └── config.py        # Конфигурация
├── tests/                   # Тесты
```

---

## 📦 Зависимости

- LangChain
- langchain-community
- openmeteo-requests
- httpx
- python-dotenv
- gradio (опционально для UI)

---

## 🧪 Пример CLI

```
> Какая погода в Тбилиси?

🌤️ Город: Тбилиси
📍 Координаты: 41.7151, 44.8271
🌡️ Температура: 29.4°C
💨 Ветер: 3.6 м/с
```

```