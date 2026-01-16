# TERAG Demo Data

Этот каталог содержит demo данные для тестирования TERAG.

## Файлы:

- `mfo_clients_sample.json` - Примеры клиентов MFO (20 клиентов, включая похожих для тестирования Auto Linker)
- `transactions_sample.json` - Примеры транзакций (50 транзакций за последние 30 дней)

## Использование:

1. **Auto Linker Demo**: Загрузите `mfo_clients_sample.json` в Streamlit app для тестирования связывания клиентов
2. **Fraud Detection Demo**: Используйте транзакции для тестирования детекции мошенничества

## Генерация новых данных:

```bash
python scripts/generate_demo_data.py
```

Это создаст новые случайные данные в `data/demo/`.
