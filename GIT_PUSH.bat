@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo Git Push to GitHub
echo ========================================
echo.
echo This will push to: origin/feature/it-compliance
echo.
pause
echo.
echo Pushing...
echo.

git push -u origin feature/it-compliance

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Open: https://github.com/sda2604/kari-weekly-dashboard
    echo 2. Create Pull Request
    echo 3. Merge to main
    echo.
) else (
    echo.
    echo ========================================
    echo ERROR!
    echo ========================================
    echo.
    echo If authentication required:
    echo 1. GitHub Token: https://github.com/settings/tokens
    echo 2. Generate token with 'repo' access
    echo 3. Use token as password
    echo.
)

pause
