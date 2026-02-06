@echo off
chcp 65001 >nul
REM =========================================================
REM   KARI FULL PIPELINE - Генерация + Рассылка
REM   Полный цикл автоматизации еженедельных отчётов
REM =========================================================

echo.
echo =========================================================
echo   KARI WEEKLY REPORT - FULL AUTOMATION PIPELINE
echo =========================================================
echo   Дата: %date% %time%
echo =========================================================
echo.

cd /d "%~dp0"

REM Создаём лог
set LOG_DIR=logs
set LOG_FILE=%LOG_DIR%\pipeline_%date:~-4,4%%date:~-7,2%%date:~-10,2%.log
mkdir %LOG_DIR% 2>nul

echo [%date% %time%] PIPELINE STARTED >> %LOG_FILE%

REM =========================================================
REM   ШАГ 1: Генерация дашборда из Excel
REM =========================================================
echo.
echo [1/2] Генерация дашборда из Excel...
echo [%date% %time%] Step 1: Generating dashboard >> %LOG_FILE%

python generate_dashboard.py >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo       ОШИБКА: Генерация не удалась!
    echo [%date% %time%] ERROR: Dashboard generation failed >> %LOG_FILE%
    goto :error
)

echo       OK - Дашборд создан
echo [%date% %time%] Step 1: SUCCESS >> %LOG_FILE%

REM =========================================================
REM   ШАГ 2: Отправка в Telegram
REM =========================================================
echo.
echo [2/2] Отправка в Telegram...
echo [%date% %time%] Step 2: Sending to Telegram >> %LOG_FILE%

cd telegram_bot
python send_dashboard.py >> ..\%LOG_FILE% 2>&1
cd ..

if errorlevel 1 (
    echo       ОШИБКА: Отправка не удалась!
    echo [%date% %time%] ERROR: Telegram send failed >> %LOG_FILE%
    goto :error
)

echo       OK - Отправлено в Telegram
echo [%date% %time%] Step 2: SUCCESS >> %LOG_FILE%

REM =========================================================
REM   УСПЕХ
REM =========================================================
echo.
echo =========================================================
echo   PIPELINE ЗАВЕРШЁН УСПЕШНО!
echo =========================================================
echo.
echo   - Дашборд: output\dashboard_current.html
echo   - Лог: %LOG_FILE%
echo   - Telegram: отправлено
echo.
echo =========================================================
echo [%date% %time%] PIPELINE COMPLETED SUCCESSFULLY >> %LOG_FILE%
goto :end

:error
echo.
echo =========================================================
echo   PIPELINE ЗАВЕРШЁН С ОШИБКОЙ
echo   Проверьте лог: %LOG_FILE%
echo =========================================================
echo [%date% %time%] PIPELINE FAILED >> %LOG_FILE%

:end
echo.
pause
