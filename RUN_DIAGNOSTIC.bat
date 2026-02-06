@echo off
echo ========================================================
echo    KARI OUTLOOK MACRO - DIAGNOSTIC TOOL
echo ========================================================
echo.
PowerShell -ExecutionPolicy Bypass -File "%~dp0diagnostic.ps1"
