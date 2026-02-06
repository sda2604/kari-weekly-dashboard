# PowerShell script to setup Task Scheduler for KARI Dashboard
# Run as Administrator for best results

$TaskName = "KARI_Dashboard_AutoSend"
$TaskPath = "\"
$Description = "Automatic weekly dashboard send to Telegram every Monday at 9:00"

# Path to the batch file
$BatPath = "C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов\auto_send_telegram.bat"
$WorkDir = "C:\Users\salni\Desktop\Данные для Claude\WORK\2025-01-22_Автоматизация_еженедельных_отчетов"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$TaskName' already exists. Removing old task..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

# Create trigger - Weekly on Monday at 9:00
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM

# Create action - Run the batch file
$Action = New-ScheduledTaskAction -Execute $BatPath -WorkingDirectory $WorkDir

# Create settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Register the task
Register-ScheduledTask -TaskName $TaskName -Trigger $Trigger -Action $Action -Settings $Settings -Description $Description

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Task Scheduler configured successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Task Name: $TaskName"
Write-Host "Schedule: Every Monday at 9:00 AM"
Write-Host "Action: $BatPath"
Write-Host ""
Write-Host "To test, run: " -NoNewline
Write-Host "Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Cyan
Write-Host ""
