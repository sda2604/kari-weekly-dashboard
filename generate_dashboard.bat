@echo off
chcp 65001 >nul
echo.
echo ===================================================
echo   KARI DASHBOARD GENERATOR
echo ===================================================
echo.

cd /d "%~dp0"

echo [%date% %time%] Запуск генерации дашборда...
python generate_dashboard.py

if errorlevel 1 (
    echo.
    echo ОШИБКА: Генерация дашборда завершилась с ошибкой
    pause
    exit /b 1
)

echo.
echo ===================================================
echo   ГОТОВО! Дашборд создан
echo ===================================================
echo.
echo Файл: output\dashboard_current.html
echo.
pause
