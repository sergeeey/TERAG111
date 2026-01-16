# 🚀 TERAG Mission Quick Start Guide

## Проверка компонентов перед запуском

Перед запуском миссии обязательно проверь все компоненты:

```powershell
cd D:\TERAG111-1\installer
.\check_mission_components.ps1
```

Этот скрипт проверит:
1. ✅ Brave API Key
2. ✅ Python и необходимые модули
3. ✅ Ollama (запущен и доступен)
4. ✅ Neo4j (контейнер запущен и доступен)
5. ✅ Конфигурация миссии

## Настройка компонентов

### 1. Brave API Key

```powershell
# Установить ключ (требует перезапуска PowerShell)
setx BRAVE_API_KEY "your-brave-api-key-here"

# Или временно для текущей сессии
$env:BRAVE_API_KEY = "your-brave-api-key-here"
```

**Где получить ключ:** [brave.com/search/api](https://brave.com/search/api)

### 2. Ollama

```powershell
# Проверить, запущен ли Ollama
ollama serve

# Или проверить в другом терминале
curl http://localhost:11434/api/tags
```

### 3. Neo4j

```powershell
# Проверить контейнер
docker ps | findstr neo4j

# Если не запущен, запустить
cd E:\TERAG
docker compose up -d neo4j

# Проверить подключение
docker exec -it terag-neo4j cypher-shell -u neo4j -p terag_local "RETURN 1"
```

## Запуск миссии

### Базовая проверка (dry-run)

```powershell
python start_mission.py --config ./data/mission_signals.yaml --dry-run
```

### Полный запуск

```powershell
python start_mission.py --config ./data/mission_signals.yaml
```

### С verbose логированием

```powershell
python start_mission.py --config ./data/mission_signals.yaml --verbose
```

## Результаты миссии

После выполнения миссии результаты будут в:

- **Рефлексия:** `E:\TERAG\data\daily_reflection.md`
- **Отчёт об открытиях:** `E:\TERAG\data\discoveries_report.md`
- **Граф знаний:** Neo4j (через http://localhost:7474)
- **Метрики:** Prometheus (http://localhost:9090) и Grafana (http://localhost:3000)

## Автоматический запуск

### Включить ежедневную миссию

```powershell
# Запусти PowerShell от имени администратора
cd D:\TERAG111-1\installer
.\rebuild_api.ps1 -InstallPath "E:\TERAG" -EnableSignalMission
```

Миссия будет запускаться автоматически каждый день в 3:00 AM.

### Проверить задачу в Task Scheduler

```powershell
# Через PowerShell
Get-ScheduledTask -TaskName "TERAG Signal Discovery Mission"

# Или через GUI
taskschd.msc
```

## Устранение проблем

### Ошибка: "Python not found"

```powershell
# Установи Python с python.org или используй из PATH
python --version

# Или укажи полный путь
C:\Python\python.exe start_mission.py --config ./data/mission_signals.yaml
```

### Ошибка: "Brave API key not configured"

```powershell
# Проверь переменную окружения
echo $env:BRAVE_API_KEY

# Если пусто, установи
setx BRAVE_API_KEY "your-key"
# Перезапусти PowerShell!
```

### Ошибка: "Ollama not accessible"

```powershell
# Проверь, запущен ли Ollama
Get-Process ollama -ErrorAction SilentlyContinue

# Если нет, запусти
ollama serve

# Или проверь порт
Test-NetConnection -ComputerName localhost -Port 11434
```

### Ошибка: "Neo4j connection failed"

```powershell
# Проверь контейнер
docker ps | findstr neo4j

# Проверь логи
docker logs terag-neo4j

# Перезапусти контейнер
docker compose restart neo4j
```

### Ошибка: "Module not found"

```powershell
# Установи недостающие модули
pip install pyyaml requests neo4j

# Или установи все зависимости
pip install -r app/requirements.txt
```

## Полезные команды

### Просмотр логов миссии

```powershell
# Последние записи
Get-Content mission_runner.log -Tail 50

# Поиск ошибок
Select-String -Path mission_runner.log -Pattern "ERROR"
```

### Проверка метрик

```powershell
# Prometheus
curl http://localhost:9090/api/v1/query?query=terag_new_concepts_total

# Grafana
# Открой http://localhost:3000 и перейди в дашборд "TERAG LLM Monitoring"
```

### Просмотр графа знаний

```powershell
# Открой Neo4j Browser
Start-Process "http://localhost:7474"

# Или через cypher-shell
docker exec -it terag-neo4j cypher-shell -u neo4j -p terag_local
```

## Следующие шаги

1. ✅ Проверь все компоненты: `.\check_mission_components.ps1`
2. ✅ Настрой Brave API Key
3. ✅ Запусти первую миссию: `python start_mission.py --config ./data/mission_signals.yaml`
4. ✅ Проверь результаты в `E:\TERAG\data\daily_reflection.md`
5. ✅ Включи автоматический запуск: `.\rebuild_api.ps1 -EnableSignalMission`

---

**Готово!** TERAG теперь может автоматически обнаруживать и записывать новые знания в граф. 🧠


















