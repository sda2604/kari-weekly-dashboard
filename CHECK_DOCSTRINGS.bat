@echo off
chcp 65001 >nul
echo ================================================
echo ПРОВЕРКА DOCSTRINGS
echo ================================================
echo.

cd /d "%~dp0"
python check_docstrings.py

echo.
echo ================================================
pause
