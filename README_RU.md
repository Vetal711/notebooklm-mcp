# Сервер NotebookLM MCP v1.0

*Read this in other languages: [English](README.md)*

Готовый к продакшену, полностью асинхронный сервер протокола Model Context Protocol (MCP) для Google NotebookLM.

Этот сервер выступает в роли моста между ИИ-агентами (такими как Claude Desktop, Cursor, Antigravity) и сервисом NotebookLM, позволяя вашему ИИ читать ваши блокноты, взаимодействовать с источниками и генерировать отчеты.

## Особенности

- **Асинхронное выполнение**: Полностью использует `asyncio` для обработки большого количества одновременных запросов.
- **Надежность**: Все консольные команды NotebookLM (CLI) обернуты в тайм-ауты с правильной обработкой ошибок.
- **Потокобезопасность (Очередь команд)**: Множественные одновременные запросы безопасно выстраиваются в очередь через `asyncio.Lock()`.
- **Продвинутые инструменты MCP**: Включает в себя `create_notebook`, `delete_notebook`, `add_source`, `list_sources`, `get_source_text`, `generate_audio`, `generate_report` и `get_history`.
- **Мультиязычность (i18n)**: Вся документация к инструментам написана на английском языке, что обеспечивает идеальную совместимость с любой LLM в мире.
- **Сетевой режим (SSE Transport)**: Поддерживает как стандартный ввод-вывод (локально), так и SSE (передача по сети).
- **Кэширование и повторные попытки**: Временные сбои CLI автоматически повторяются. Операции чтения кэшируются.
- **Диагностика**: Встроенный инструмент `health_check()` для проверки доступности CLI и статуса авторизации.

---

## Установка

Вы можете установить этот сервер автоматически (рекомендуется) или вручную.

### Метод А: Автоматическая установка в один клик (Рекомендуется)

Этот метод автоматически настраивает виртуальное окружение, скачивает все зависимости (включая `notebooklm-py` и браузер Chromium для авторизации) и регистрирует сервер в ваших IDE (Claude Desktop, Cursor, Antigravity).

1. Скачайте или клонируйте этот репозиторий:
   ```bash
   git clone https://github.com/Vetal711/notebooklm-mcp.git
   cd notebooklm-mcp
   ```

2. Запустите скрипт автоматической установки:
   - **Windows**: Дважды кликните по файлу `install.bat` (или запустите его в терминале).
   - **Mac/Linux**: Запустите `bash install.sh`

3. Авторизуйтесь в Google:
   Как только установка завершится, необходимо авторизовать консольную утилиту. Запустите следующую команду и следуйте инструкциям в открывшемся браузере:
   - **Windows**: `venv\Scripts\notebooklm.exe login`
   - **Mac/Linux**: `./venv/bin/notebooklm login`

4. Перезапустите вашу IDE/Агента (Claude Desktop, Cursor или Antigravity), и сервер будет готов к работе!

---

### Метод Б: Ручная установка

Если вы предпочитаете настраивать всё вручную или использовать глобальное окружение Python:

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/Vetal711/notebooklm-mcp.git
   cd notebooklm-mcp
   ```

2. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv venv
   # На Windows:
   venv\Scripts\pip install -e .
   # На Mac/Linux:
   ./venv/bin/pip install -e .
   ```

3. Установите браузерный движок Playwright (нужен для входа):
   ```bash
   # На Windows:
   venv\Scripts\playwright install chromium
   # На Mac/Linux:
   ./venv/bin/playwright install chromium
   ```

4. Авторизуйтесь:
   ```bash
   # На Windows:
   venv\Scripts\notebooklm.exe login
   # На Mac/Linux:
   ./venv/bin/notebooklm login
   ```

5. **Ручная конфигурация для MCP-клиентов**:
   Вместо запуска скрипта автоматической конфигурации, вы можете вручную добавить следующий JSON-блок в файл настроек вашего MCP-клиента (например, `claude_desktop_config.json`, `cline_mcp_settings.json` или `mcp_config.json`).
   
   *Обязательно замените `/absolute/path/to/notebooklm-mcp` на реальный абсолютный путь к папке с клонированным репозиторием на вашем ПК.*

   ```json
   {
     "mcpServers": {
       "NotebookLM": {
         "command": "/absolute/path/to/notebooklm-mcp/venv/bin/notebooklm-mcp",
         "args": []
       }
     }
   }
   ```
   *(Примечание для Windows: Используйте путь `venv\\Scripts\\notebooklm-mcp.exe` и экранируйте обратные слеши двумя слешами).*

   **Важно:** Сервер автоматически сгенерирует файл `.env` в корневой папке при первом запуске (или при установке), чтобы управлять абсолютными путями.

---

### Развертывание в Docker

Для сборки и запуска через Docker:
```bash
docker build -t notebooklm-mcp .
docker run -i --rm -v ~/.notebooklm:/root/.notebooklm notebooklm-mcp
```
*(Примечание: Вам необходимо примонтировать папку с конфигурацией `.notebooklm`, чтобы пробросить вашу локальную сессию авторизации внутрь контейнера).*
