@echo off
echo ================================================================
echo   FIX: Replace personal paths with placeholders
echo ================================================================
echo.

set CLONE_DIR=%USERPROFILE%\Desktop\kari-weekly-dashboard

if not exist "%CLONE_DIR%" (
    echo ERROR: Repo folder not found at %CLONE_DIR%
    echo Run PUSH_TO_GITHUB.bat first
    pause
    exit /b 1
)

echo [1/3] Updating macro_v5.txt...

set MACRO_FILE=%CLONE_DIR%\outlook_vba\macro_v5.txt
set MACRO_SRC=%~dp0OUTLOOK_VBA_v5.txt

REM Read source file line by line and replace paths
powershell -Command "(Get-Content '%MACRO_SRC%' -Encoding UTF8) -replace 'C:\\Users\\salni\\Desktop\\[^\"]+\\input\\', 'C:\Users\YOUR_USER\YOUR_PROJECT_FOLDER\input\' -replace 'C:\\Users\\salni\\Desktop\\[^\"]+\\logs\\', 'C:\Users\YOUR_USER\YOUR_PROJECT_FOLDER\logs\' | Set-Content '%MACRO_FILE%' -Encoding UTF8"

echo Done.
echo.
echo [2/3] Git commit...

cd /d "%CLONE_DIR%"
git add -A
git diff --cached --stat
echo.
git commit -m "security: replace personal paths with placeholders in VBA macro"

echo.
echo [3/3] Pushing to GitHub...

git push origin main

if errorlevel 1 (
    echo ERROR: Push failed.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   DONE! Paths replaced with placeholders.
echo   Check: https://github.com/sda2604/kari-weekly-dashboard
echo ================================================================
pause
