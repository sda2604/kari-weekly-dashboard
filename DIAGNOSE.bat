@echo off
echo ====================================================================
echo         DIAGNOSE PYTHON AND LIBRARIES
echo ====================================================================
echo.

echo [1] Checking Python in PATH...
echo.
python --version
if errorlevel 1 (
    echo ERROR: Python not found in PATH!
    goto :end
)
echo.

echo [2] Python location:
where python
echo.

echo [3] Python executable path:
python -c "import sys; print('Python path:', sys.executable)"
echo.

echo [4] Checking pandas:
python -c "import pandas; print('OK pandas:', pandas.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: pandas NOT installed in this Python!
    echo.
    echo Installing now...
    echo.
    python -m pip install pandas openpyxl requests
) else (
    echo OK: pandas installed
)

echo.
echo [5] Checking openpyxl:
python -c "import openpyxl; print('OK openpyxl:', openpyxl.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: openpyxl NOT installed
) else (
    echo OK: openpyxl installed
)

echo.
echo [6] Checking requests:
python -c "import requests; print('OK requests:', requests.__version__)" 2>nul
if errorlevel 1 (
    echo ERROR: requests NOT installed
) else (
    echo OK: requests installed
)

echo.
echo ====================================================================
echo [7] Testing generate_dashboard.py directly:
echo ====================================================================
echo.

cd /d "%~dp0"
python generate_dashboard.py

:end
echo.
echo ====================================================================
echo Press any key to exit
pause >nul
