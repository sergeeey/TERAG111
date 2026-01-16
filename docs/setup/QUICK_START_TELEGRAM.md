# 🚀 Быстрый старт Telegram сервиса

## ✅ Что уже готово

- ✅ `telegram_service.py` создан
- ✅ Настройки добавлены в `.env`
- ✅ Mission template создан
- ✅ Systemd unit файл готов

## 📦 Шаг 1: Установите зависимости

```bash
pip install aiogram APScheduler python-dotenv httpx
```

Или обновите все зависимости:
```bash
pip install -r requirements.txt
```

## 🧪 Шаг 2: Протестируйте подключение

```bash
python scripts/tests/test_telegram_service.py
```

Должно прийти тестовое сообщение в Telegram.

## 🚀 Шаг 3: Запустите сервис

```bash
python src/integration/telegram_service.py
```

Сервис запустится и начнёт слушать команды.

## 📱 Шаг 4: Протестируйте команды

В Telegram отправьте боту:

1. `/start` — список команд
2. `/status` — быстрый статус
3. `/find ai governance` — быстрый поиск
4. `/health` — полный health-check

## ⚙️ Настройки в `.env`

Все настройки уже добавлены:
```bash
TELEGRAM_BOT_TOKEN=8010267972:AAFVfgd1e__Mkb6Z9NdWc_WGN-uecucUTGQ
TELEGRAM_CHAT_ID=792610846
TELEGRAM_WHITELIST=792610846
TERAG_DAILY_REPORT_HOUR=9
TERAG_DAILY_REPORT_MINUTE=0
TERAG_MAX_CONCURRENT_MISSIONS=3
```

## 🔄 Автозапуск (опционально)

### Windows (Task Scheduler)

Создайте задачу, которая запускает:
```
python D:\TERAG111-1\src\integration\telegram_service.py
```

### Linux (Systemd)

1. Скопируйте `terag-telegram.service` в `/etc/systemd/system/`
2. Обновите пути в файле
3. Выполните:
```bash
sudo systemctl daemon-reload
sudo systemctl enable terag-telegram
sudo systemctl start terag-telegram
```

## 📚 Полная документация

См. `TELEGRAM_SERVICE_README.md` для детальной информации.

---

**Готово!** TERAG теперь полноценный оператор через Telegram! 🎯✨













