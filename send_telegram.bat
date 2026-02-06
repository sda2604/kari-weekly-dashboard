@echo off
REM Скрипт для рассылки дашборда KARI через Telegram

echo.
echo ===================================================
echo    РАССЫЛКА ДАШБОРДА KARI ЧЕРЕЗ TELEGRAM
echo ===================================================
echo.

cd /d "%~dp0telegram_bot"

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не найден!
    echo Установи Python: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден
echo.

REM Проверка наличия библиотек
echo Проверяю библиотеки...
python -c "import telegram" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Библиотека python-telegram-bot не установлена
    echo Устанавливаю...
    pip install python-telegram-bot
    echo.
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Библиотека requests не установлена
    echo Устанавливаю...
    pip install requests
    echo.
)

echo ✅ Библиотеки готовы
echo.

REM Проверка наличия config.py
if not exist "config.py" (
    echo ❌ ОШИБКА: Файл config.py не найден!
    echo Путь: %CD%\config.py
    echo.
    pause
    exit /b 1
)

echo ✅ Конфигурация найдена
echo.

REM Проверка наличия дашборда
if not exist "..\output\dashboard_current.html" (
    echo ❌ ОШИБКА: Дашборд не найден!
    echo Путь: %CD%\..\output\dashboard_current.html
    echo Создай дашборд: output\dashboard_current.html
    echo.
    pause
    exit /b 1
)

echo ✅ Дашборд найден
echo.
echo ===================================================
echo    ЗАПУСКАЮ РАССЫЛКУ...
echo ===================================================
echo.

REM Запуск рассылки
python send_dashboard.py

echo.
echo ===================================================
echo.
echo Рассылка завершена!
echo Проверь Telegram - дашборд должен прийти.
echo.
pause
