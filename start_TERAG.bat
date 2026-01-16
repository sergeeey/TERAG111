@echo off
REM TERAG AI System - Quick Launcher
REM Автоматический запуск TERAG одним кликом

echo.
echo ====================================
echo   TERAG AI System
echo ====================================
echo.

REM Переходим в директорию проекта
cd /d "%~dp0"

echo Starting TERAG...
echo.

REM Запускаем API сервер в новом окне
start "TERAG API Server" powershell -NoExit -Command "python scripts/run_api.py"

REM Ждём запуска сервера
timeout /t 5 /nobreak >nul

REM Открываем дашборд в браузере
start http://127.0.0.1:8000/api/static/index.html

echo.
echo TERAG is starting...
echo Dashboard will open in your browser automatically
echo.
echo API Server: http://127.0.0.1:8000
echo Dashboard:  http://127.0.0.1:8000/api/static/index.html
echo.
echo Press any key to close this window
echo (Closing this window will NOT stop the server)
pause >nul



























