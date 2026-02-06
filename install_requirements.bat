@echo off
REM Установка необходимых библиотек для Telegram бота

echo.
echo ===================================================
echo    УСТАНОВКА БИБЛИОТЕК ДЛЯ TELEGRAM БОТА
echo ===================================================
echo.

echo Устанавливаю python-telegram-bot...
pip install python-telegram-bot

echo.
echo Устанавливаю requests...
pip install requests

echo.
echo Устанавливаю openpyxl (для чтения Excel)...
pip install openpyxl

echo.
echo ===================================================
echo ✅ ВСЕ БИБЛИОТЕКИ УСТАНОВЛЕНЫ
echo ===================================================
echo.

pause
