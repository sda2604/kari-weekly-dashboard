@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ========================================
echo Git Status Check
echo ========================================
echo.

git status
echo.
echo ========================================
echo Git Log (last commit)
echo ========================================
git log -1 --oneline
echo.
echo ========================================
echo Ready to push?
echo ========================================
echo.
echo Run: git push -u origin feature/it-compliance
echo.
pause
