# Emergency Runbook: Data Corruption

## Симптомы

- Неожиданные ошибки при чтении данных из Neo4j
- Некорректные результаты запросов
- Ошибки валидации данных

## Диагностика

### Шаг 1: Проверить целостность данных

```bash
# Проверить Neo4j database
neo4j-admin check-database

# Проверить логи на ошибки
grep -i "corrupt\|invalid\|malformed" logs/neo4j.log
```

### Шаг 2: Проверить последние изменения

```cypher
// В Neo4j Browser
MATCH (n)
WHERE n.created_at > datetime() - duration({days: 1})
RETURN n
LIMIT 100
```

## Восстановление

### Вариант 1: Восстановление из backup

1. Остановить TERAG API
2. Восстановить Neo4j из последнего backup:
   ```bash
   neo4j-admin restore --from=/backup/neo4j/latest
   ```
3. Перезапустить Neo4j
4. Проверить целостность
5. Запустить TERAG API

### Вариант 2: Переключение на backup Neo4j

Если primary поврежден, переключиться на backup:

1. Установить backup переменные окружения
2. Перезапустить TERAG API
3. Восстановить primary из backup позже

### Вариант 3: Частичное восстановление

Если повреждена только часть данных:

1. Экспортировать корректные данные:
   ```cypher
   CALL apoc.export.cypher.all('backup.cypher')
   ```

2. Удалить поврежденные узлы/связи
3. Импортировать из backup

## Профилактика

- Регулярные backup (ежедневно)
- Проверка целостности (еженедельно)
- Мониторинг аномалий в данных

## Контакты

- Tech Lead: @sergey
- Database Admin: @current_team
- Emergency: Telegram channel #terag-alerts
