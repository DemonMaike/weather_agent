Отлично! Ниже — аналогичная инструкция для **Linux/macOS** в стиле твоего примера для Windows.

---

# Weather Agent 🌤️

MCP-сервер для прогноза погоды, реализованный через FastMCP.

## Возможности

* 🌍 Поиск города по названию (геокодинг через Nominatim)
* 🌤️ Актуальные погодные данные (через Open-Meteo)
* 📅 Прогноз погоды на 1–7 дней
* 📍 Геокоординаты и информация о часовом поясе
* 🔑 Без необходимости в API-ключах

---

## Требования

* Python 3.11+
* Менеджер окружений: `venv`, `uv`, `conda`
* Claude Desktop или Cursor

---

## Установка и запуск

### 1. Инициализация окружения

Выбери один из способов:

#### 🔹 Вариант 1: Через `venv` (встроенный)

```bash
cd "/путь/до/Weather Agent"
python3 -m venv .venv
```

#### 🔹 Вариант 2: Через `uv`

```bash
cd "/путь/до/Weather Agent"
uv venv
```

#### 🔹 Вариант 3: Через `conda`

```bash
conda create -n weather-agent python=3.11
conda activate weather-agent
```

---

### 2. Установка зависимостей

Если используешь `venv` или `conda`:

```bash
# Активация окружения:
source .venv/bin/activate

# Установка зависимостей:
pip install -r requirements.txt
```

Если используешь `uv`:

```bash
uv pip install -r requirements.txt
```

---

### 3. Получение абсолютных путей

Для настройки конфигурации тебе понадобятся:

#### 🔹 Абсолютный путь до интерпретатора:

```bash
realpath .venv/bin/python
```

#### 🔹 Абсолютный путь до `weather_server.py`:

```bash
realpath weather_server.py
```

---

### 4. Пример конфигурации Claude Desktop

Добавь следующий блок в файл `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "weather-agent": {
      "command": "/полный/путь/до/.venv/bin/python",
      "args": [
        "/полный/путь/до/weather_server.py"
      ],
      "env": {
        "PYTHONPATH": "/полный/путь/до/Weather Agent/src"
      }
    }
  }
}
```

---

## Пример на Linux/macOS

```json
{
  "mcpServers": {
    "weather-agent": {
      "command": "/home/user/projects/weather-agent/.venv/bin/python",
      "args": [
        "/home/user/projects/weather-agent/weather_server.py"
      ],
      "env": {
        "PYTHONPATH": "/home/user/projects/weather-agent/src"
      }
    }
  }
}
```

---

## Расположение конфигурационных файлов

### Claude Desktop

* **macOS/Linux**: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Cursor

* **macOS/Linux**: `~/Library/Application Support/Cursor/User/globalStorage/anysphere.cursor/config.json`

---

## После настройки

1. Полностью перезапусти MCP-клиент (Claude Desktop или Cursor)
2. Убедись, что появилась иконка 🔨
3. Попробуй ввести: **"Какая погода в Москве?"**

---

## Примеры запросов

* *"Какая погода в Москве?"*
* *"Покажи недельный прогноз для Нью-Йорка"*
* *"Температура в Лондоне завтра"*
* *"Прогноз в Токио на 3 дня"*

---

## Отладка и тестирование

```bash
# Запуск сервера вручную (в активированном окружении)
python weather_server.py
```

---

## Структура проекта

```
Weather Agent/
├── src/
│   ├── weather_mcp/
│   │   ├── server.py          # FastMCP сервер
│   │   └── tools/
│   │       ├── geo.py         # Геокодинг
│   │       └── weather.py     # Получение прогноза
│   └── utils/
│       └── config.py          # Конфигурация
├── weather_server.py          # Точка входа
└── pyproject.toml             # Зависимости
```

---

Если хочешь, могу сгенерировать всё это как `README.md`.
