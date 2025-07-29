# Weather Agent 🌤️

LLM-агент для получения прогноза погоды по названию города.

---

## ✅ Возможности

- 🌍 Поиск координат по названию города (геокодинг через Nominatim)
- 🌤️ Получение актуального прогноза погоды (через Open-Meteo)
- 🧠 LLM-интерфейс на базе Gemini
- 🔄 CLI и UI интерфейсы с использованием LangChain React Agent
- ⚙️ MCP сервер для подключения к Claude Desktop и Cursor AI

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
# Обязательные переменные для запуска CLI и UI
GOOGLE_API_KEY=your_gemini_api_key
LLM_MODEL=gemini-2.0-flash
```

Вы можете указать её в `.env` или экспортировать вручную в окружение.

### 🖥️ Запуск

#### CLI

```bash
python cli_run.py
```
<img width="1177" height="339" alt="image" src="https://github.com/user-attachments/assets/afb6766e-a08f-49b1-8565-68f35ba2d224" />


#### GUI

```bash
python gui_run.py
```
<img width="1406" height="633" alt="image" src="https://github.com/user-attachments/assets/d973a14e-7de6-40b2-a28e-9ac3ce70a4cf" />


#### MCP конфигурация

Для удобства настройки MCP клиентов (Claude Desktop, Cursor AI) в проекте есть скрипт:

```bash
python mcp_config_init.py
```

Он автоматически создаст корректный конфиг с учётом вашей операционной системы, путей к Python интерпретатору и серверному скрипту, а также содержит инструкцию по настройке MCP клиента.

Запустите скрипт, следуйте подсказкам — и получите готовый конфиг для подключения агента к MCP клиенту.
<img width="857" height="111" alt="image" src="https://github.com/user-attachments/assets/eb821f0a-4f73-4ad3-8c6e-5687232bbea9" />
<img width="951" height="554" alt="image" src="https://github.com/user-attachments/assets/1b282c1c-bba8-4cfd-99c5-de1918580456" />


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
🗣️ Начинаем интерактивный чат...

🧑 Вы: Привет, подскажешь погоду в Тбилиси?
🤖 Агент обрабатывает запрос...
💭 Обработка: Привет, подскажешь погоду в Тбилиси?    

🤖 Агент: Конечно, скажите, на сколько дней вам нужен прогноз?

🧑 Вы: на один день но на послезавтра 
🤖 Агент обрабатывает запрос...
💭 Обработка: на один день но на послезавтра

🤖 Агент: Простите, я не могу предоставить прогноз на 
конкретный день, я могу предоставить прогноз на 1-7 дн
ей, начиная с сегодняшнего дня. Хотите узнать прогноз на ближайший день?

🧑 Вы: давай на 3 дня
🤖 Агент обрабатывает запрос...
💭 Обработка: давай на 3 дня

🤖 Агент: Вот прогноз погоды в Тбилиси на ближайшие 3 дня:

Сегодня: температура от 24.1°C до 33.8°C, без осадков, максимальная скорость ветра 14.0 км/ч.
Завтра: температура от 23.7°C до 35.7°C, без осадков, максимальная скорость ветра 11.7 км/ч.
Послезавтра: температура от 24.4°C до 34.8°C, осадки 0.1 мм, максимальная скорость ветра 9.4 км/ч.

```

## Задачи
- [ ] **Баг** react_agent.py не работает команда clear(🐛 Ошибка очистки памяти: 'InMemorySaver' object has no attribute 'adelete_state')
- [ ] Поправить\дописать тесты
-  [ ] Redis для кеширования запросов
