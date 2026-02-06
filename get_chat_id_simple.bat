@echo off
REM Простой скрипт для получения chat_id

echo.
echo ===================================================
echo    ПОЛУЧЕНИЕ CHAT_ID (ПРОСТОЙ СПОСОБ)
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

python simple_get_id.py

pause
