@echo off
chcp 65001 >nul
echo.
echo ===================================================
echo   CREATING TASK SCHEDULER TASK FOR KARI DASHBOARD
echo ===================================================
echo.

REM Delete existing task if exists
schtasks /delete /tn "KARI_Dashboard_AutoSend" /f >nul 2>&1

REM Create new scheduled task
REM Weekly on Monday at 9:00 AM
schtasks /create /tn "KARI_Dashboard_AutoSend" /tr "\"%~dp0auto_send_telegram.bat\"" /sc weekly /d MON /st 09:00 /ru "%USERNAME%" /rl HIGHEST /f

if errorlevel 1 (
    echo.
    echo ERROR: Failed to create scheduled task
    echo Please run this script as Administrator
    pause
    exit /b 1
)

echo.
echo ===================================================
echo   SUCCESS! Task created successfully
echo ===================================================
echo.
echo Task Name: KARI_Dashboard_AutoSend
echo Schedule: Every Monday at 9:00 AM
echo.
echo To test manually, run:
echo   schtasks /run /tn "KARI_Dashboard_AutoSend"
echo.
echo To check status:
echo   schtasks /query /tn "KARI_Dashboard_AutoSend"
echo.

REM Show task status
echo Current task status:
schtasks /query /tn "KARI_Dashboard_AutoSend" /fo list

pause
