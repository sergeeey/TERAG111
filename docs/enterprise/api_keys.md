# TERAG API Keys Guide

## Создание API ключа

```bash
python scripts/cli/create_api_key.py \
  --client-id CLIENT-001 \
  --role analyst \
  --expires-days 365
```

## Роли

- **admin**: Полный доступ, 200 req/min
- **analyst**: Read-only + queries, 100 req/min
- **client**: API-only, 50 req/min

## Использование API ключа

```bash
curl -X GET http://localhost:8000/api/v2/query \
  -H "Authorization: Bearer sk_terag_prod_..."
```

## Отзыв ключа

```python
from src.security.api_auth import TeragAuth

auth = TeragAuth()
auth.revoke_key("sk_terag_prod_...")
```

## Безопасность

- Ключи хранятся в MongoDB с bcrypt хешированием
- Оригинальный ключ показывается только один раз при создании
- Рекомендуется ротация ключей каждые 90 дней
