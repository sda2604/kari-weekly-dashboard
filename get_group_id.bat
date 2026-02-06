@echo off
REM Скрипт для получения ID группы Telegram

echo.
echo ===================================================
echo    ПОЛУЧЕНИЕ ID ГРУППЫ TELEGRAM
echo ===================================================
echo.

cd /d "%~dp0telegram_bot"

REM Проверка requests
python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo Устанавливаю библиотеку requests...
    pip install requests
    echo.
)

python get_group_id.py

pause
