import os
import sys
import json
from pathlib import Path

def main():
    interpreter = sys.executable
    script_path = Path("mcp_weather_server.py").resolve()

    if not script_path.exists():
        print(f"[❌] Файл {script_path} не найден. Убедитесь, что скрипт находится в папке с этим генератором.")
        return

    print("🔧 Выберите клиента MCP:")
    print("1 — Claude Desktop")
    print("2 — Cursor AI")
    choice = input("Введите номер (1 или 2): ").strip()

    if choice not in {"1", "2"}:
        print("❌ Неверный выбор.")
        return

    config = {
        "mcpServers": {
            "weather-agent": {
                "command": interpreter,
                "args": [str(script_path)],
                "env": {}
            }
        }
    }

    json_output = json.dumps(config, indent=2)

    print("\n✅ Сгенерирован конфиг:\n")
    print(json_output)

    if choice == "1":
        print("\n📌 Вставьте это в файл `claude_desktop_config.json` в разделе `mcpServers`.")
        print("Путь к файлу:")
        print("  - Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
        print("  - macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
        print("  - Linux: ~/.config/Claude/claude_desktop_config.json")
        print("\n💡 В интерфейсе Claude Desktop:")
        print("  1. Откройте меню 'Claude' > 'Settings...'.")
        print("  2. Перейдите на вкладку 'Developer'.")
        print("  3. Нажмите 'Edit Config' для открытия конфигурационного файла.")
        print("  4. Вставьте сгенерированный JSON в раздел `mcpServers`.")

    else:
        print("\n📌 Вставьте это в файл `.cursor/mcp.json` в разделе `mcpServers`.")
        print("Путь к файлу:")
        print("  - Глобально: ~/.cursor/mcp.json")
        print("  - Локально в проекте: ./project/.cursor/mcp.json")
        print("\n💡 В интерфейсе Cursor AI:")
        print("  1. Перейдите в 'File' > 'Cursor Settings'.")
        print("  2. Выберите вкладку 'MCP'.")
        print("  3. Нажмите 'Add New Global MCP Server' или 'Add New Project MCP Server'.")
        print("  4. Вставьте сгенерированный JSON в соответствующий раздел.")

    # Дополнительно можно сохранить в файл, если нужно:
    save = input("💾 Хотите сохранить файл (y/n)? ").strip().lower()
    if save == "y":
        fname = "mcp_config.json"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(json_output)
        print(f"✅ Конфиг сохранён как {fname}")

if __name__ == "__main__":
    main()
