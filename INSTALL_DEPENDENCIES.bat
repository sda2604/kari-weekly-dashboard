@echo off
chcp 65001 >nul
echo ====================================================================
echo         УСТАНОВКА БИБЛИОТЕК ДЛЯ KARI DASHBOARD
echo ====================================================================
echo.
echo Устанавливаю необходимые Python библиотеки...
echo.

REM Проверка что Python установлен
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ОШИБКА: Python не найден!
    echo.
    echo Убедись что Python установлен и добавлен в PATH
    echo.
    pause
    exit /b 1
)

echo ✅ Python найден:
python --version
echo.

echo ====================================================================
echo Устанавливаю библиотеки...
echo ====================================================================
echo.

REM Устанавливаем все необходимые библиотеки
echo [1/4] pandas - обработка Excel файлов
python -m pip install pandas --quiet --upgrade
if errorlevel 1 (
    echo ❌ Ошибка установки pandas
    pause
    exit /b 1
)
echo ✅ pandas установлен

echo.
echo [2/4] openpyxl - работа с .xlsx файлами
python -m pip install openpyxl --quiet --upgrade
if errorlevel 1 (
    echo ❌ Ошибка установки openpyxl
    pause
    exit /b 1
)
echo ✅ openpyxl установлен

echo.
echo [3/4] requests - отправка в Telegram
python -m pip install requests --quiet --upgrade
if errorlevel 1 (
    echo ❌ Ошибка установки requests
    pause
    exit /b 1
)
echo ✅ requests установлен

echo.
echo [4/4] python-telegram-bot - Telegram бот (опционально)
python -m pip install python-telegram-bot --quiet --upgrade
if errorlevel 1 (
    echo ⚠️  Предупреждение: python-telegram-bot не установлен (не критично)
) else (
    echo ✅ python-telegram-bot установлен
)

echo.
echo ====================================================================
echo              ПРОВЕРКА УСТАНОВЛЕННЫХ БИБЛИОТЕК
echo ====================================================================
echo.

python -c "import pandas; print('✅ pandas:', pandas.__version__)"
python -c "import openpyxl; print('✅ openpyxl:', openpyxl.__version__)"
python -c "import requests; print('✅ requests:', requests.__version__)"

echo.
echo ====================================================================
echo                    УСТАНОВКА ЗАВЕРШЕНА!
echo ====================================================================
echo.
echo Теперь можно запускать тест: test\RUN_TEST.bat
echo.
pause
