# Emergency Runbook: LLM Failure

## Симптомы

- Ошибки при запросах к LLM (Ollama/LM Studio)
- Timeout при генерации ответов
- Telegram alerts о LLM ошибках

## Диагностика

### Шаг 1: Проверить LLM сервис

```bash
# Проверить Ollama
curl http://localhost:11434/api/tags

# Проверить LM Studio
curl http://localhost:1234/v1/models
```

### Шаг 2: Проверить переменные окружения

```bash
echo $LLM_PROVIDER
echo $LLM_URL
echo $LLM_MODEL
```

## Восстановление

### Вариант 1: Перезапуск LLM сервиса

```bash
# Ollama
systemctl restart ollama
# или
docker restart ollama

# LM Studio
# Перезапустить приложение вручную
```

### Вариант 2: Переключение на другой провайдер

1. Изменить переменные окружения:
   ```bash
   export LLM_PROVIDER="ollama"  # или "lmstudio"
   export LLM_URL="http://localhost:11434"
   export LLM_MODEL="qwen2.5:7b-instruct"
   ```

2. Перезапустить TERAG API

### Вариант 3: Fallback на простой режим

Если LLM полностью недоступен, система может работать в режиме без LLM (только граф знаний).

## Мониторинг

- Health check endpoint: `/api/health`
- LLM status в метриках: `/api/metrics`
- Telegram alerts при критических ошибках

## Контакты

- Tech Lead: @sergey
- Emergency: Telegram channel #terag-alerts
