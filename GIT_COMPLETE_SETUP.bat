@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo Git Full Setup and Push
echo ========================================
echo.

:: Step 1: Initialize Git
echo [1/5] Initializing Git...
git init
if %errorlevel% neq 0 (
    echo ERROR: Failed to init git
    pause
    exit /b 1
)
echo [OK] Git initialized
echo.

:: Step 2: Add remote
echo [2/5] Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/sda2604/kari-weekly-dashboard.git
if %errorlevel% neq 0 (
    echo ERROR: Failed to add remote
    pause
    exit /b 1
)
echo [OK] Remote added
echo.

:: Step 3: Fetch main
echo [3/5] Fetching main branch...
git fetch origin main
echo [OK] Fetched
echo.

:: Step 4: Checkout new branch
echo [4/5] Creating branch feature/it-compliance...
git checkout -b feature/it-compliance 2>nul
if %errorlevel% neq 0 (
    git checkout feature/it-compliance
)
echo [OK] Branch ready
echo.

:: Step 5: Stage all files
echo [5/5] Staging files...
git add .
echo [OK] Files staged
echo.

:: Commit
echo Creating commit...
git commit -m "feat: IT-Compliance refactoring (v2.2.0)" -m "- Secrets moved to .env" -m "- Structured JSON logging" -m "- Centralized error handling" -m "- Data validation" -m "- Google Style docstrings" -m "- Retry mechanism for Telegram API" -m "- Graceful degradation" -m "- CHANGELOG.md" -m "- requirements.txt" -m "" -m "IT Standards compliance: 41%% -> 90%%+"

if %errorlevel% neq 0 (
    echo [WARNING] Nothing to commit or error
)
echo [OK] Commit ready
echo.

:: Push
echo ========================================
echo Ready to push!
echo ========================================
echo.
echo This will push to: origin/feature/it-compliance
echo.
pause
echo.
echo Pushing to GitHub...
echo.

git push -u origin feature/it-compliance

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS!
    echo ========================================
    echo.
    echo Branch pushed to GitHub!
    echo.
    echo Next steps:
    echo 1. Open: https://github.com/sda2604/kari-weekly-dashboard
    echo 2. Click: "Compare and pull request"
    echo 3. Create PR and Merge
    echo.
) else (
    echo.
    echo ========================================
    echo PUSH FAILED
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Need authentication
    echo    - Username: sda2604
    echo    - Password: GitHub Personal Access Token
    echo    - Get token: https://github.com/settings/tokens
    echo.
    echo 2. Network issue
    echo.
    echo 3. Permission denied
    echo.
)

pause
