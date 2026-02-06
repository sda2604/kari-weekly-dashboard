@echo off
REM Скрипт для получения chat_id пользователей Telegram

echo.
echo ===================================================
echo    ПОЛУЧЕНИЕ CHAT_ID ПОЛЬЗОВАТЕЛЕЙ
echo ===================================================
echo.

cd /d "%~dp0telegram_bot"

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не найден!
    pause
    exit /b 1
)

REM Проверка наличия библиотеки
python -c "import telegram" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  ВНИМАНИЕ: Библиотека python-telegram-bot не установлена
    echo Устанавливаю...
    pip install python-telegram-bot
    echo.
)

REM Проверка config.py
if not exist "config.py" (
    echo ❌ ОШИБКА: Файл config.py не найден!
    pause
    exit /b 1
)

echo ✅ Запускаю бота для сбора chat_id...
echo.
echo ИНСТРУКЦИЯ:
echo 1. Открой бота в Telegram
echo 2. Отправь команду /start
echo 3. Бот покажет твой chat_id
echo 4. Для остановки нажми Ctrl+C
echo.

REM Запуск бота
python get_chat_id.py

pause
