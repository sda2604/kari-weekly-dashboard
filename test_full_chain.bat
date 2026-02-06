@echo off
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║     KARI - ПОЛНОЕ ТЕСТИРОВАНИЕ ЦЕПОЧКИ АВТОМАТИЗАЦИИ       ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║  Дата: %date% %time%                                ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

set ERRORS=0
set LOG_FILE=logs\test_chain_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%.log
mkdir logs 2>nul

echo [%date% %time%] НАЧАЛО ТЕСТИРОВАНИЯ >> %LOG_FILE%
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ШАГ 1/5: Проверка Excel файлов в input/
echo ═══════════════════════════════════════════════════════════════
echo.

set EXCEL_COUNT=0
for /r input %%f in (*.xlsx *.xls) do (
    echo   [OK] %%~nxf
    set /a EXCEL_COUNT+=1
)

if %EXCEL_COUNT% GTR 0 (
    echo.
    echo   ✓ Найдено Excel файлов: %EXCEL_COUNT%
    echo [OK] Excel files found: %EXCEL_COUNT% >> %LOG_FILE%
) else (
    echo   ✗ ВНИМАНИЕ: Excel файлы не найдены в input/
    echo [WARNING] No Excel files in input/ >> %LOG_FILE%
    set /a ERRORS+=1
)
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ШАГ 2/5: Проверка Python и библиотек
echo ═══════════════════════════════════════════════════════════════
echo.

python --version 2>nul
if errorlevel 1 (
    echo   ✗ Python не найден!
    echo [ERROR] Python not found >> %LOG_FILE%
    set /a ERRORS+=1
) else (
    echo   ✓ Python установлен
    echo [OK] Python installed >> %LOG_FILE%
)

python -c "import pandas; print('  ✓ pandas:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo   ✗ pandas не установлен
    echo [ERROR] pandas not installed >> %LOG_FILE%
    set /a ERRORS+=1
)

python -c "import openpyxl; print('  ✓ openpyxl:', openpyxl.__version__)" 2>nul
if errorlevel 1 (
    echo   ✗ openpyxl не установлен
    echo [ERROR] openpyxl not installed >> %LOG_FILE%
    set /a ERRORS+=1
)

python -c "import telegram; print('  ✓ telegram:', telegram.__version__)" 2>nul
if errorlevel 1 (
    echo   ✗ python-telegram-bot не установлен
    echo [ERROR] python-telegram-bot not installed >> %LOG_FILE%
    set /a ERRORS+=1
)
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ШАГ 3/5: Генерация дашборда
echo ═══════════════════════════════════════════════════════════════
echo.

echo   Запускаю generate_dashboard.py...
python generate_dashboard.py >> %LOG_FILE% 2>&1

if errorlevel 1 (
    echo   ✗ ОШИБКА генерации дашборда!
    echo [ERROR] Dashboard generation failed >> %LOG_FILE%
    set /a ERRORS+=1
) else (
    if exist "output\dashboard_current.html" (
        for %%A in (output\dashboard_current.html) do (
            echo   ✓ Дашборд создан: %%~zA байт
        )
        echo [OK] Dashboard generated >> %LOG_FILE%
    ) else (
        echo   ✗ Файл дашборда не создан!
        echo [ERROR] Dashboard file not created >> %LOG_FILE%
        set /a ERRORS+=1
    )
)
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ШАГ 4/5: Проверка Telegram конфигурации
echo ═══════════════════════════════════════════════════════════════
echo.

if exist "telegram_bot\config.py" (
    echo   ✓ config.py существует
    findstr /c:"BOT_TOKEN" telegram_bot\config.py >nul
    if errorlevel 1 (
        echo   ✗ BOT_TOKEN не найден в config.py
        set /a ERRORS+=1
    ) else (
        echo   ✓ BOT_TOKEN настроен
    )
    echo [OK] Telegram config exists >> %LOG_FILE%
) else (
    echo   ✗ telegram_bot\config.py не найден!
    echo [ERROR] Telegram config not found >> %LOG_FILE%
    set /a ERRORS+=1
)
echo.

echo ═══════════════════════════════════════════════════════════════
echo   ШАГ 5/5: Тестовая отправка в Telegram
echo ═══════════════════════════════════════════════════════════════
echo.

echo   Отправить тестовое сообщение в Telegram? (Y/N)
set /p SEND_TEST="> "

if /i "%SEND_TEST%"=="Y" (
    echo.
    echo   Отправляю...
    cd telegram_bot
    python send_dashboard.py >> ..\%LOG_FILE% 2>&1
    cd ..
    
    if errorlevel 1 (
        echo   ✗ ОШИБКА отправки в Telegram!
        echo [ERROR] Telegram send failed >> %LOG_FILE%
        set /a ERRORS+=1
    ) else (
        echo   ✓ Отправлено в Telegram
        echo [OK] Telegram send successful >> %LOG_FILE%
    )
) else (
    echo   Пропущено
    echo [SKIP] Telegram test skipped >> %LOG_FILE%
)
echo.

echo ═══════════════════════════════════════════════════════════════
echo   РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ
echo ═══════════════════════════════════════════════════════════════
echo.

if %ERRORS%==0 (
    echo   ╔════════════════════════════════════════╗
    echo   ║  ✓ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!         ║
    echo   ╚════════════════════════════════════════╝
    echo.
    echo   Цепочка автоматизации работает полностью.
    echo   Можно настроить Task Scheduler для автозапуска.
    echo [SUCCESS] All tests passed >> %LOG_FILE%
) else (
    echo   ╔════════════════════════════════════════╗
    echo   ║  ✗ ОБНАРУЖЕНЫ ОШИБКИ: %ERRORS%                      ║
    echo   ╚════════════════════════════════════════╝
    echo.
    echo   Проверьте лог: %LOG_FILE%
    echo [FAILED] Errors found: %ERRORS% >> %LOG_FILE%
)

echo.
echo [%date% %time%] ТЕСТИРОВАНИЕ ЗАВЕРШЕНО >> %LOG_FILE%
echo.
echo Лог сохранён: %LOG_FILE%
echo.
pause
