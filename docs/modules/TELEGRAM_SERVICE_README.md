# 📲 TERAG Telegram Service — Полная инструкция

## ✅ Что уже сделано

- ✅ `telegram_service.py` создан в `src/integration/`
- ✅ Зависимости добавлены в `requirements.txt` (aiogram, APScheduler)
- ✅ Настройки добавлены в `.env`
- ✅ Mission template создан в `missions/osint_deep_template.yaml`

## 🚀 Быстрый старт

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

Или только для Telegram:
```bash
pip install aiogram APScheduler python-dotenv httpx
```

### 2. Проверьте настройки в `.env`

Убедитесь, что в `.env` есть:
```bash
TELEGRAM_BOT_TOKEN=8010267972:AAFVfgd1e__Mkb6Z9NdWc_WGN-uecucUTGQ
TELEGRAM_CHAT_ID=792610846
TELEGRAM_WHITELIST=792610846
TERAG_DAILY_REPORT_HOUR=9
TERAG_DAILY_REPORT_MINUTE=0
TERAG_MAX_CONCURRENT_MISSIONS=3
TERAG_MISSION_RUNNER=python installer/start_mission.py
TERAG_HEALTHCHECK_CMD=python check_terag_full_stack.py
```

### 3. Запустите сервис

```bash
python src/integration/telegram_service.py
```

Сервис запустится и начнёт слушать команды в Telegram.

## 📱 Доступные команды

### Базовые команды

- `/start` или `/help` — показать список команд
- `/status` — быстрый статус системы (20 сек)
- `/health` — полный health-check отчёт (до 2 минут)

### Поиск и миссии

- `/find <query>` — быстрый OSINT-поиск через Brave Search (3 результата)
- `/deep_search <query>` — запуск полноценной миссии (сбор → анализ → граф)
- `/run_mission <name>` — запуск миссии по имени из `installer/data/`

### Управление

- `/cancel <mission_name>` — попытка отменить миссию (best effort)

## 🕐 Ежедневные отчёты

Сервис автоматически отправляет ежедневный Cognitive Ops Report в указанное время (по умолчанию 9:00).

Чтобы изменить время, обновите в `.env`:
```bash
TERAG_DAILY_REPORT_HOUR=9
TERAG_DAILY_REPORT_MINUTE=0
```

## 🔒 Безопасность

### Whitelist

Только пользователи из whitelist могут использовать команды:
```bash
TELEGRAM_WHITELIST=792610846,123456789  # через запятую
```

Если whitelist пуст — доступ открыт для всех (только для разработки!).

### Rate Limiting

- Максимум одновременных миссий: `TERAG_MAX_CONCURRENT_MISSIONS=3`
- Таймауты: health-check (180 сек), миссии (30-60 минут)

## 🧪 Тестирование

### 1. Проверка подключения

Отправьте боту `/start` — он должен ответить списком команд.

### 2. Проверка статуса

Отправьте `/status` — должен прийти краткий отчёт о состоянии системы.

### 3. Быстрый поиск

Отправьте `/find ai governance` — должны прийти топ-3 результата из Brave Search.

### 4. Health-check

Отправьте `/health` — должен прийти полный отчёт (может занять до 2 минут).

## 🐳 Запуск в фоне (Systemd)

Создайте файл `/etc/systemd/system/terag-telegram.service`:

```ini
[Unit]
Description=TERAG Telegram Service
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/TERAG111-1
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/python3 /path/to/TERAG111-1/src/integration/telegram_service.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable terag-telegram
sudo systemctl start terag-telegram
sudo systemctl status terag-telegram
```

## 🐳 Docker (альтернатива)

Создайте `docker-compose.telegram.yml`:

```yaml
version: '3.8'
services:
  telegram:
    build: .
    command: python src/integration/telegram_service.py
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - TELEGRAM_WHITELIST=${TELEGRAM_WHITELIST}
    volumes:
      - ./.env:/app/.env
    restart: unless-stopped
```

## 📊 Примеры сообщений

### Daily Report (с OSINT дайджестом)

```
🧠 TERAG Cognitive Ops Report — 2025-11-07T09:00:00

✅ lm_studio: latency=5.10s, models=2
✅ brave_search
✅ bright_data
❌ neo4j: connection failed

• To run mission: /run_mission daily_osint
• To do a quick find: /find <query>
• To run deep search: /deep_search <query>

🔍 OSINT Digest

Топ-3 новых сигнала:

1. 🔥 Novel Cognitive Architecture
   New approach to cognitive reasoning using graph-based knowledge representation
   новизна: 0.85, уверенность: 0.78
   [Источник](https://arxiv.org/abs/2025.12345)

2. ⭐ AI Governance Framework
   Emerging framework for ethical AI governance in enterprise environments
   новизна: 0.72, уверенность: 0.81
   [Источник](https://example.com/ai-governance)

3. 💡 Weak Signal Detection
   Novel methodology for detecting weak signals in large-scale data streams
   новизна: 0.68, уверенность: 0.75
   [Источник](https://example.com/weak-signals)

Тренды:
• Высокая новизна сигналов
• Высокая уверенность

Статистика: Средняя новизна: 0.75, Средняя уверенность: 0.78, Всего сигналов: 3

Топ источники: arxiv.org, example.com
```

### Mission Finish

```
✅ Mission `deep_search_1700000000` finished.

Output:
```
[mission output here]
```
```

## ⚠️ Ограничения

1. **Отмена задач** — `/cancel` работает best effort, для надёжной отмены нужно доработать `run_mission.py`
2. **Прямой чат с LM Studio** — не реализован (можно добавить с лимитами)
3. **UI для выбора миссий** — можно расширить с inline keyboard

## 🔧 Troubleshooting

### Бот не отвечает

1. Проверьте, что сервис запущен: `ps aux | grep telegram_service`
2. Проверьте логи: смотрите вывод консоли или логи systemd
3. Проверьте токен: `echo $TELEGRAM_BOT_TOKEN`

### Команды не работают

1. Проверьте whitelist: убедитесь, что ваш Chat ID в списке
2. Проверьте права: бот должен иметь доступ к файлам миссий
3. Проверьте зависимости: `pip list | grep aiogram`

### Health-check не работает

1. Убедитесь, что `check_terag_full_stack.py` сохраняет JSON
2. Проверьте путь: файл должен быть в корне проекта
3. Проверьте права на запись файла

## 📝 Следующие шаги

После успешного запуска:

1. ✅ Протестируйте все команды
2. ✅ Настройте ежедневные отчёты
3. ✅ Добавьте в автозапуск (systemd/docker)
4. ✅ Настройте мониторинг и логирование

---

**Готово!** TERAG теперь полноценный оператор через Telegram! 🎯✨

