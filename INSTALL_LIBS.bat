@echo off
echo ====================================================================
echo     FORCE INSTALL PYTHON LIBRARIES
echo ====================================================================
echo.
echo Installing libraries for all Python versions...
echo.

cd /d "%~dp0"

echo.
echo ====================================================================
echo Method 1: Install via python
echo ====================================================================
python -m pip install --user pandas openpyxl requests python-telegram-bot
echo.

echo ====================================================================
echo Method 2: Install via py (Python Launcher)
echo ====================================================================
py -m pip install --user pandas openpyxl requests python-telegram-bot 2>nul
echo.

echo ====================================================================
echo Method 3: Install via pip directly
echo ====================================================================
pip install --user pandas openpyxl requests python-telegram-bot 2>nul
echo.

echo ====================================================================
echo Checking result
echo ====================================================================
echo.
python -c "import pandas; print('OK pandas:', pandas.__version__)"
python -c "import openpyxl; print('OK openpyxl:', openpyxl.__version__)"
python -c "import requests; print('OK requests:', requests.__version__)"

echo.
echo ====================================================================
echo If you see library versions above - installation successful!
echo ====================================================================
echo.
pause
