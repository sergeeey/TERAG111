# Настройка мониторинга для TERAG

## Sentry.io (Error Tracking)

### Шаг 1: Создать аккаунт на Sentry.io
1. Перейти на https://sentry.io
2. Создать бесплатный аккаунт (free tier: 5,000 events/month)
3. Создать новый проект (выбрать Python → FastAPI)

### Шаг 2: Получить DSN
1. В настройках проекта скопировать DSN
2. Добавить в `.env`:
   ```
   SENTRY_DSN=https://your-dsn@sentry.io/project-id
   ```

### Шаг 3: Установить зависимость
```bash
pip install sentry-sdk
```

### Шаг 4: Проверить работу
Sentry автоматически инициализируется при запуске сервера.
Ошибки будут автоматически отправляться в Sentry.

## Better Uptime (Uptime Monitoring)

### Шаг 1: Создать аккаунт
1. Перейти на https://betteruptime.com
2. Создать бесплатный аккаунт (free tier: 10 monitors)
3. Создать новый monitor

### Шаг 2: Настроить мониторинг
1. URL для мониторинга: `https://your-terag-api.com/health`
2. Interval: 5 minutes
3. Alert channels: Email, Telegram (если настроен)

### Шаг 3: Настроить алерты
- Email уведомления при недоступности
- Telegram уведомления (опционально)

## Telegram Alerts (для критических ошибок)

### Уже настроено
Telegram alerts уже интегрированы в:
- `src/core/error_handler.py` - для ошибок Neo4j
- `src/integration/telegram_service.py` - общий сервис

### Настройка
1. Добавить в `.env`:
   ```
   TELEGRAM_BOT_TOKEN=your-bot-token
   TELEGRAM_CHAT_ID=your-chat-id
   ```

## CloudWatch (Basic Logs) - Опционально

### Для AWS развертывания
1. Настроить CloudWatch Logs
2. Добавить логирование через boto3
3. Настроить retention policy (7 дней для free tier)

## Проверка мониторинга

### Тест Sentry
```python
# В коде добавить тестовую ошибку
import sentry_sdk
sentry_sdk.capture_message("Test error from TERAG")
```

### Тест Better Uptime
1. Остановить сервер временно
2. Проверить, что Better Uptime обнаружил недоступность
3. Запустить сервер
4. Проверить, что статус восстановлен

### Тест Telegram Alerts
1. Симулировать ошибку Neo4j (отключить Neo4j)
2. Проверить, что Telegram alert отправлен

## Рекомендации

1. **Sentry**: Использовать для всех ошибок в production
2. **Better Uptime**: Настроить для основного health endpoint
3. **Telegram**: Использовать для критических алертов (Neo4j down, MongoDB down)
4. **CloudWatch**: Использовать только если развертывание на AWS

## Стоимость

- **Sentry**: Free tier (5,000 events/month) - достаточно для начала
- **Better Uptime**: $5/мес (10 monitors) - минимальный план
- **Telegram**: Бесплатно
- **CloudWatch**: Free tier (5GB logs, 7 days retention)

**Итого**: ~$5/мес для базового мониторинга
