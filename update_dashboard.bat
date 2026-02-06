@echo off
REM Скрипт автоматического версионирования дашборда KARI
REM Использование: update_dashboard.bat

setlocal EnableDelayedExpansion

set OUTPUT_DIR=%~dp0output
set ARCHIVE_DIR=%~dp0output\archive
set CURRENT=dashboard_current.html

echo.
echo ===================================================
echo    СИСТЕМА ВЕРСИОНИРОВАНИЯ ДАШБОРДА KARI
echo ===================================================
echo.

REM Создать archive если нет
if not exist "%ARCHIVE_DIR%" (
    mkdir "%ARCHIVE_DIR%"
    echo ✓ Папка архива создана: output\archive
) else (
    echo ✓ Папка архива готова: output\archive
)
echo.

REM Если текущий дашборд существует - переместить в архив
if exist "%OUTPUT_DIR%\%CURRENT%" (
    REM Получить timestamp
    for /f "tokens=1-4 delims=/ " %%a in ('date /t') do (
        set DATE=%%c-%%b-%%a
    )
    for /f "tokens=1-2 delims=: " %%a in ('time /t') do (
        set TIME=%%a-%%b
    )
    set TIMESTAMP=!DATE!_!TIME!
    
    REM Переместить файл
    move "%OUTPUT_DIR%\%CURRENT%" "%ARCHIVE_DIR%\!TIMESTAMP!.html" >nul
    echo ✓ Старая версия сохранена: archive\!TIMESTAMP!.html
) else (
    echo ℹ Текущего дашборда нет (первый запуск)
)
echo.

REM Удалить старые версии (оставить только 10 последних)
set COUNT=0
for %%F in ("%ARCHIVE_DIR%\*.html") do set /a COUNT+=1

if !COUNT! GTR 10 (
    set /a REMOVED=!COUNT!-10
    
    REM Удалить самые старые файлы
    set /a KEEP=0
    for /f "delims=" %%F in ('dir /b /o-d "%ARCHIVE_DIR%\*.html"') do (
        set /a KEEP+=1
        if !KEEP! GTR 10 (
            del "%ARCHIVE_DIR%\%%F"
        )
    )
    
    echo ✓ Архив очищен (удалено !REMOVED! старых версий)
) else (
    echo ℹ В архиве !COUNT! версий (лимит 10)
)

echo.
echo ===================================================
echo ✓ ГОТОВО! Теперь создавай новый dashboard_current.html
echo ===================================================
echo.

pause
