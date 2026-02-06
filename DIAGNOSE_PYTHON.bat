@echo off
chcp 65001 >nul
echo ====================================================================
echo         ДИАГНОСТИКА PYTHON И БИБЛИОТЕК
====================================================================
echo.

echo [1] Проверяю Python в PATH...
echo.
python --version
if errorlevel 1 (
    echo ❌ Python не найден в PATH!
    goto :end
)
echo.

echo [2] Путь к Python:
where python
echo.

echo [3] Проверяю установленные библиотеки:
echo.
python -c "import sys; print('Python путь:', sys.executable)"
echo.
python -c "import sys; print('Версия:', sys.version)"
echo.

echo [4] Проверяю pandas:
python -c "import pandas; print('✅ pandas:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ pandas НЕ установлен в этом Python!
    echo.
    echo Пробую установить прямо сейчас...
    python -m pip install pandas openpyxl requests
) else (
    echo ✅ pandas установлен
)

echo.
echo [5] Проверяю openpyxl:
python -c "import openpyxl; print('✅ openpyxl:', openpyxl.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ openpyxl НЕ установлен
) else (
    echo ✅ openpyxl установлен
)

echo.
echo [6] Проверяю requests:
python -c "import requests; print('✅ requests:', requests.__version__)" 2>nul
if errorlevel 1 (
    echo ❌ requests НЕ установлен
) else (
    echo ✅ requests установлен
)

echo.
echo ====================================================================
echo [7] Пробую запустить generate_dashboard.py напрямую:
echo ====================================================================
echo.

cd /d "%~dp0"
python generate_dashboard.py

:end
echo.
echo ====================================================================
echo Нажми любую клавишу для выхода
pause >nul
