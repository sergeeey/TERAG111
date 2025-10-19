# 📅 Windows Task Scheduler Setup

## 🎯 Настройка автоматического мониторинга TERAG

### 1️⃣ Создание задачи

1. Откройте **Task Scheduler** (taskschd.msc)
2. Нажмите **Create Basic Task**
3. Название: `TERAG Health Check`
4. Описание: `Daily health check for TERAG environment`

### 2️⃣ Настройка триггера

1. **Trigger**: Daily
2. **Start**: Сегодняшняя дата
3. **Time**: 09:00 (или удобное время)
4. **Recur every**: 1 days

### 3️⃣ Настройка действия

1. **Action**: Start a program
2. **Program/script**: `powershell.exe`
3. **Add arguments**: `-ExecutionPolicy Bypass -File "D:\TERAG111-1\health-check.ps1"`
4. **Start in**: `D:\TERAG111-1`

### 4️⃣ Дополнительные настройки

1. **General** tab:
   - ✅ Run whether user is logged on or not
   - ✅ Run with highest privileges
   - ✅ Hidden

2. **Settings** tab:
   - ✅ Allow task to be run on demand
   - ✅ Run task as soon as possible after a scheduled start is missed
   - ✅ If the running task does not end when requested, force it to stop

### 5️⃣ Тестирование

```powershell
# Ручной запуск для тестирования
powershell -ExecutionPolicy Bypass -File .\health-check.ps1
```

### 6️⃣ Просмотр логов

Логи сохраняются в файл `health-check.log` в корне проекта.

## 🔧 Альтернативная настройка через PowerShell

```powershell
# Создание задачи через PowerShell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"D:\TERAG111-1\health-check.ps1`""
$trigger = New-ScheduledTaskTrigger -Daily -At 9am
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest

Register-ScheduledTask -TaskName "TERAG Health Check" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily health check for TERAG environment"
```

## 📊 Мониторинг

### Что проверяется:
- ✅ Ollama сервер
- ✅ Python окружение
- ✅ ChromaDB база данных
- ✅ RAG функциональность
- ✅ Критические файлы проекта

### Уведомления:
- Логи сохраняются в `health-check.log`
- Ошибки выводятся в консоль
- Можно настроить email уведомления

## 🆘 Устранение проблем

### Задача не запускается:
1. Проверьте права доступа
2. Убедитесь, что PowerShell доступен
3. Проверьте путь к скрипту

### Скрипт не работает:
1. Запустите вручную для диагностики
2. Проверьте логи в `health-check.log`
3. Убедитесь, что все зависимости установлены

---

**Автоматический мониторинг TERAG настроен!** 📅✅
