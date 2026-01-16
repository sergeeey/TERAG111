# TERAG Billing Setup Guide

## Обзор

TERAG Billing система использует MongoDB для хранения данных о клиентах, использовании и инвойсах.

## Настройка MongoDB

1. Установите MongoDB или используйте MongoDB Atlas
2. Настройте переменные окружения:
   ```bash
   export MONGODB_URI="mongodb://localhost:27017/"
   export MONGODB_DATABASE="terag_billing"
   ```

## Создание клиента

```bash
python scripts/cli/create_api_key.py --client-id CLIENT-001 --role analyst
```

## Генерация инвойсов

Инвойсы генерируются автоматически каждый месяц через cron job или вручную через API:

```bash
curl -X POST http://localhost:8000/api/v2/billing/invoices/generate \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": "CLIENT-001",
    "period_start": "2026-01-01T00:00:00",
    "period_end": "2026-01-31T23:59:59"
  }'
```

## Интеграция платежей

### Stripe

1. Получите API ключи от Stripe
2. Настройте переменные окружения:
   ```bash
   export STRIPE_SECRET_KEY="sk_test_..."
   export STRIPE_WEBHOOK_SECRET="whsec_..."
   ```

### Kaspi

1. Получите API ключи от Kaspi
2. Настройте переменные окружения:
   ```bash
   export KASPI_API_KEY="your_kaspi_key"
   export KASPI_API_URL="https://api.kaspi.kz/v1"
   ```

## Мониторинг

- Grafana dashboard: `/api/v2/billing/metrics`
- Логи: `logs/billing.log`
