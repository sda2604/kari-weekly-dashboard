@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo Git Setup for IT-Compliance v2.2.0
echo ========================================
echo.
echo This will:
echo - Initialize Git locally
echo - Fetch existing repo from GitHub
echo - Create feature branch
echo - Commit all changes
echo - Push to GitHub
echo.
pause
echo.

:: Step 1: Init
echo [1/7] Initializing Git...
if exist ".git" (
    echo [SKIP] Already initialized
) else (
    git init
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to init
        pause
        exit /b 1
    )
    echo [OK] Initialized
)
echo.

:: Step 2: Configure (optional but recommended)
echo [2/7] Configuring Git...
git config user.name "salni" 2>nul
git config user.email "salnikov.d2604@gmail.com" 2>nul
echo [OK] Configured
echo.

:: Step 3: Add remote
echo [3/7] Setting up remote...
git remote remove origin 2>nul
git remote add origin https://github.com/sda2604/kari-weekly-dashboard.git
if %errorlevel% neq 0 (
    echo [ERROR] Failed to add remote
    pause
    exit /b 1
)
echo [OK] Remote added
echo.

:: Step 4: Fetch main
echo [4/7] Fetching main branch from GitHub...
git fetch origin main
if %errorlevel% neq 0 (
    echo [WARNING] Could not fetch main
    echo [INFO] Will create orphan branch
)
echo [OK] Fetched
echo.

:: Step 5: Create branch
echo [5/7] Creating feature branch...
git checkout -b feature/it-compliance 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Branch exists, switching...
    git checkout feature/it-compliance
)
echo [OK] On branch feature/it-compliance
echo.

:: Step 6: Stage and commit
echo [6/7] Staging files...
git add .
echo [OK] Files staged
echo.

echo Creating commit...
git commit -m "feat: IT-Compliance refactoring (v2.2.0)" -m "- Secrets moved to .env" -m "- Structured JSON logging" -m "- Centralized error handling" -m "- Data validation" -m "- Google Style docstrings" -m "- Retry mechanism" -m "- Graceful degradation" -m "- CHANGELOG.md" -m "- requirements.txt" -m "" -m "IT Standards: 41%% -> 90%%+"

if %errorlevel% equ 0 (
    echo [OK] Commit created
) else (
    echo [INFO] Nothing to commit or already committed
)
echo.

:: Step 7: Push
echo [7/7] Pushing to GitHub...
echo.
echo ========================================
echo IMPORTANT: GitHub Authentication
echo ========================================
echo.
echo Username: sda2604
echo Password: [GitHub Personal Access Token]
echo.
echo If you don't have a token:
echo 1. Visit: https://github.com/settings/tokens
echo 2. Generate new token (classic)
echo 3. Select: repo (full control)
echo 4. Copy token and use as password
echo.
pause
echo.

git push -u origin feature/it-compliance

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Branch pushed to GitHub
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Open: https://github.com/sda2604/kari-weekly-dashboard
    echo 2. Click: "Compare and pull request"
    echo 3. Review changes
    echo 4. Click: "Create pull request"
    echo 5. Click: "Merge pull request"
    echo.
    echo Done!
    echo.
) else (
    echo.
    echo ========================================
    echo PUSH FAILED
    echo ========================================
    echo.
    echo Common issues:
    echo.
    echo 1. Authentication failed
    echo    - Make sure you use GitHub token, not password
    echo    - Token must have 'repo' access
    echo.
    echo 2. Network error
    echo    - Check internet connection
    echo.
    echo 3. Branch already exists on remote
    echo    - Try: git push --force origin feature/it-compliance
    echo    - Or delete branch on GitHub first
    echo.
    echo Try again or contact support
    echo.
)

pause
