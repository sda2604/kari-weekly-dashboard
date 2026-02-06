@echo off
echo ================================================================
echo   PUSH KARI DASHBOARD TO GITHUB
echo ================================================================
echo.

set REPO_URL=https://github.com/sda2604/kari-weekly-dashboard.git
set PROJECT_DIR=%~dp0
set UPLOAD_DIR=%PROJECT_DIR%github_upload
set CLONE_DIR=%USERPROFILE%\Desktop\kari-weekly-dashboard

echo [1/5] Cloning repository...
echo.

if exist "%CLONE_DIR%" rmdir /s /q "%CLONE_DIR%"

git clone %REPO_URL% "%CLONE_DIR%"
if errorlevel 1 (
    echo.
    echo ERROR: Clone failed! Install git: https://git-scm.com/download/win
    pause
    exit /b 1
)

echo.
echo [2/5] Copying files...
echo.

copy /Y "%UPLOAD_DIR%\README.md" "%CLONE_DIR%\README.md"
copy /Y "%UPLOAD_DIR%\.gitignore" "%CLONE_DIR%\.gitignore"

copy /Y "%PROJECT_DIR%generate_dashboard.py" "%CLONE_DIR%\generate_dashboard.py"
copy /Y "%PROJECT_DIR%run_full_pipeline.bat" "%CLONE_DIR%\run_full_pipeline.bat"

mkdir "%CLONE_DIR%\outlook_vba" 2>nul
copy /Y "%PROJECT_DIR%OUTLOOK_VBA_v5.txt" "%CLONE_DIR%\outlook_vba\macro_v5.txt"

mkdir "%CLONE_DIR%\telegram_bot" 2>nul
copy /Y "%PROJECT_DIR%telegram_bot\send_dashboard.py" "%CLONE_DIR%\telegram_bot\send_dashboard.py"
copy /Y "%PROJECT_DIR%telegram_bot\period_parser.py" "%CLONE_DIR%\telegram_bot\period_parser.py"
copy /Y "%UPLOAD_DIR%\telegram_bot\config.example.py" "%CLONE_DIR%\telegram_bot\config.example.py"

mkdir "%CLONE_DIR%\test" 2>nul
copy /Y "%PROJECT_DIR%test\test_full_pipeline.py" "%CLONE_DIR%\test\test_full_pipeline.py"
copy /Y "%PROJECT_DIR%test\RUN_TEST.bat" "%CLONE_DIR%\test\RUN_TEST.bat"

mkdir "%CLONE_DIR%\docs" 2>nul
copy /Y "%UPLOAD_DIR%\docs\ARCHITECTURE.md" "%CLONE_DIR%\docs\ARCHITECTURE.md"

echo.
echo [3/5] Files copied. Checking...
echo.
dir /b "%CLONE_DIR%"
echo.
dir /b "%CLONE_DIR%\telegram_bot"
echo.
dir /b "%CLONE_DIR%\outlook_vba"
echo.
dir /b "%CLONE_DIR%\test"
echo.
dir /b "%CLONE_DIR%\docs"
echo.

echo [4/5] Git commit...
echo.
cd /d "%CLONE_DIR%"
git add -A
git commit -m "feat: full automation pipeline - VBA + Python + Telegram"

echo.
echo [5/5] Pushing to GitHub...
echo.
git push origin main

if errorlevel 1 (
    echo.
    echo ERROR: Push failed. GitHub may ask for auth.
    echo If token needed: github.com - Settings - Developer settings - Tokens
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================================
echo   DONE! Repository updated.
echo   Link: https://github.com/sda2604/kari-weekly-dashboard
echo ================================================================
echo.
pause
