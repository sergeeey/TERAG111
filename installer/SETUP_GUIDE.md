# 🚀 TERAG Setup Guide - Быстрая установка

## ✅ Рекомендуемый способ (простая версия)

Используйте упрощенную версию скрипта, которая гарантированно работает:

```powershell
cd D:\TERAG111-1\installer
powershell -ExecutionPolicy Bypass -File .\setup_terag_simple.ps1
```

## 🔧 Альтернатива (полная версия)

Если нужна полная версия с расширенной обработкой ошибок:

```powershell
cd D:\TERAG111-1\installer

# Очистка от проблемных кавычек
Get-Content .\setup_terag.ps1 -Raw | `
    ForEach-Object { 
        $_ -replace '"','"' `
            -replace '"','"' `
            -replace ''',"'" `
            -replace ''',"'" 
    } | `
    Set-Content .\setup_terag_clean.ps1 -Encoding UTF8

# Запуск очищенной версии
powershell -ExecutionPolicy Bypass -File .\setup_terag_clean.ps1
```

## 📋 Проверка синтаксиса

Если нужно проверить любой PowerShell скрипт:

```powershell
powershell -NoProfile -Command {
    param($file)
    try {
        [System.Management.Automation.Language.Parser]::ParseFile($file, [ref]$null, [ref]$null) | Out-Null
        Write-Host "Syntax OK" -ForegroundColor Green
    } catch {
        Write-Host "Syntax Error: $($_.Exception.Message)" -ForegroundColor Red
    }
} -ArgumentList "D:\TERAG111-1\installer\setup_terag_simple.ps1"
```

## 🎯 Что делает скрипт

1. Проверяет наличие Docker
2. Создает структуру каталогов на E:\TERAG
3. Копирует все файлы проекта
4. Обновляет конфигурацию
5. Запускает Docker Compose
6. Выводит адреса сервисов

## ⚠️ Если что-то пошло не так

1. Проверьте, что Docker Desktop запущен
2. Убедитесь, что диск E: доступен
3. Проверьте логи: `docker compose logs`
4. Используйте простую версию: `setup_terag_simple.ps1`

---

**Версия:** 1.0  
**Дата:** 2025-01-27





















