# Emergency Runbook: Neo4j Outage

## Симптомы

- Ошибки подключения к Neo4j
- Timeout при запросах к графу знаний
- Telegram alerts о критических ошибках Neo4j

## Автоматическое восстановление

Система TERAG автоматически переключается на backup Neo4j при обнаружении ошибок primary инстанса.

### Проверка статуса

1. Проверить логи:
   ```bash
   grep "Neo4j" logs/terag.log | tail -20
   ```

2. Проверить, используется ли backup:
   - В логах должно быть: "Switched to backup Neo4j"
   - Или: "using_backup: true"

## Ручное восстановление

### Шаг 1: Проверить primary Neo4j

```bash
# Проверить доступность
curl http://localhost:7474

# Проверить подключение через bolt
neo4j-admin check-connectivity
```

### Шаг 2: Если primary недоступен

1. Проверить статус сервиса:
   ```bash
   systemctl status neo4j
   # или
   docker ps | grep neo4j
   ```

2. Перезапустить Neo4j:
   ```bash
   systemctl restart neo4j
   # или
   docker restart neo4j-container
   ```

3. Проверить логи Neo4j:
   ```bash
   tail -f /var/log/neo4j/neo4j.log
   ```

### Шаг 3: Проверить backup Neo4j

```bash
# Проверить переменные окружения
echo $NEO4J_BACKUP_URI
echo $NEO4J_BACKUP_USER
echo $NEO4J_BACKUP_PASSWORD

# Проверить подключение
neo4j-admin check-connectivity --uri $NEO4J_BACKUP_URI
```

### Шаг 4: Принудительное переключение на backup

Если система не переключилась автоматически:

1. Установить переменные окружения:
   ```bash
   export NEO4J_BACKUP_URI="bolt://backup-neo4j:7687"
   export NEO4J_BACKUP_USER="neo4j"
   export NEO4J_BACKUP_PASSWORD="backup_password"
   ```

2. Перезапустить TERAG API:
   ```bash
   systemctl restart terag-api
   # или
   docker restart terag-api
   ```

### Шаг 5: Восстановление primary

После восстановления primary Neo4j:

1. Система автоматически вернется на primary при следующем успешном запросе
2. Или можно принудительно:
   - Удалить/переименовать backup переменные окружения
   - Перезапустить TERAG API

## Мониторинг

- Grafana dashboard: Neo4j Connection Status
- Telegram alerts при переключении
- Логи: `logs/terag_error_handler.log`

## Контакты

- Tech Lead: @sergey
- DevOps: @current_team
- Emergency: Telegram channel #terag-alerts
