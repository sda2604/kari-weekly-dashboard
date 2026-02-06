@echo off
REM Скрипт очистки папки output от старых файлов
REM Оставляет только dashboard_current.html и папку archive

echo ===================================================
echo ОЧИСТКА ПАПКИ OUTPUT
echo ===================================================
echo.

cd /d "%~dp0"
cd output

echo Текущая директория: %CD%
echo.

echo Удаление старых HTML файлов...
del /Q dashboard.html 2>nul
del /Q dashboard_FINAL.html 2>nul
del /Q dashboard_final_v3.html 2>nul
del /Q dashboard_ios_fixed.html 2>nul
del /Q dashboard_nnv_week.html 2>nul
del /Q dashboard_nnv_week_BACKUP.html 2>nul

echo Удаление JSON файлов...
del /Q analysis_report.json 2>nul
del /Q dashboard_data.json 2>nul
del /Q dashboard_data_clean.json 2>nul
del /Q dashboard_data_detailed.json 2>nul
del /Q dashboard_final.json 2>nul
del /Q FINAL_DASHBOARD_DATA.json 2>nul

echo.
echo ===================================================
echo ГОТОВО!
echo ===================================================
echo.
echo В папке output осталось:
dir /B

pause
