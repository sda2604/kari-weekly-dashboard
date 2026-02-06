@echo off
chcp 65001 >nul
echo =========================================================
echo   KARI DASHBOARD - MANUAL RUN
echo =========================================================
echo.

cd /d "%~dp0"

echo [1/2] Generating dashboard...
python generate_dashboard.py

if errorlevel 1 (
    echo ERROR: Dashboard generation failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Sending to Telegram...
cd telegram_bot
python send_dashboard.py
cd ..

if errorlevel 1 (
    echo ERROR: Telegram send failed!
    pause
    exit /b 1
)

echo.
echo =========================================================
echo   SUCCESS!
echo =========================================================
echo   Dashboard sent to Telegram
echo.
pause
