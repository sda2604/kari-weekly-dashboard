@echo off
REM Скрипт для автоматического запуска рассылки дашборда
REM Используется Task Scheduler для еженедельного запуска

echo.
echo ===================================================
echo   АВТОМАТИЧЕСКАЯ РАССЫЛКА ДАШБОРДА KARI
echo ===================================================
echo.
echo Запущено: %date% %time%
echo.

REM Переходим в директорию проекта
cd /d "%~dp0"

REM Логирование
set LOG_FILE=logs\telegram_send_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log
mkdir logs 2>nul

echo [%date% %time%] Начало рассылки >> %LOG_FILE%

REM Запуск рассылки
cd telegram_bot
python send_dashboard.py >> ..\%LOG_FILE% 2>&1

if errorlevel 1 (
    echo [%date% %time%] ОШИБКА: Рассылка завершилась с ошибкой >> ..\%LOG_FILE%
    exit /b 1
) else (
    echo [%date% %time%] Рассылка успешно завершена >> ..\%LOG_FILE%
)

echo.
echo ===================================================
echo   ГОТОВО
echo ===================================================
echo.
