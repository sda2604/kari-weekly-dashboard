# KARI Outlook Macro - Automatic Diagnostic Tool
# Encoding: UTF-8

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   KARI OUTLOOK MACRO - AUTO DIAGNOSTIC" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

$projectPath = $PSScriptRoot
$inputPath = Join-Path $projectPath "input"
$logsPath = Join-Path $projectPath "logs"
$macroFile = Join-Path $projectPath "OUTLOOK_VBA_v6_ENCODING_FIX.txt"

# Check 1: Project Structure
Write-Host "[1/6] Checking project structure..." -ForegroundColor Yellow
if (Test-Path $inputPath) {
    Write-Host "  OK - input/ folder exists" -ForegroundColor Green
} else {
    Write-Host "  ERROR - input/ folder not found!" -ForegroundColor Red
}

if (Test-Path $logsPath) {
    Write-Host "  OK - logs/ folder exists" -ForegroundColor Green
} else {
    Write-Host "  WARNING - logs/ folder not found, creating..." -ForegroundColor Yellow
    New-Item -Path $logsPath -ItemType Directory | Out-Null
}

# Check 2: Macro File
Write-Host ""
Write-Host "[2/6] Checking macro file..." -ForegroundColor Yellow
if (Test-Path $macroFile) {
    Write-Host "  OK - Macro file found" -ForegroundColor Green
    $macroContent = Get-Content $macroFile -Raw -Encoding UTF8
    if ($macroContent -match "GetSubjectSafe") {
        Write-Host "  OK - GetSubjectSafe function found (v6.0)" -ForegroundColor Green
    } else {
        Write-Host "  ERROR - GetSubjectSafe not found! Wrong version?" -ForegroundColor Red
    }
} else {
    Write-Host "  ERROR - Macro file not found!" -ForegroundColor Red
}

# Check 3: Today's Log
Write-Host ""
Write-Host "[3/6] Checking today's log..." -ForegroundColor Yellow
$today = Get-Date -Format "yyyyMMdd"
$logFile = Join-Path $logsPath "outlook_macro_$today.log"

if (Test-Path $logFile) {
    Write-Host "  OK - Log file found: outlook_macro_$today.log" -ForegroundColor Green
    
    $logContent = Get-Content $logFile -Raw -Encoding UTF8
    $emailCount = ([regex]::Matches($logContent, "=== NEW EMAIL ===")).Count
    $matchCount = ([regex]::Matches($logContent, "MATCH: YES")).Count
    $skipCount = ([regex]::Matches($logContent, "MATCH: NO")).Count
    
    Write-Host "  Emails processed: $emailCount" -ForegroundColor Cyan
    Write-Host "  Matched: $matchCount" -ForegroundColor Green
    Write-Host "  Skipped: $skipCount" -ForegroundColor Yellow
    
    if ($matchCount -gt 0) {
        Write-Host "  OK - Macro is catching emails!" -ForegroundColor Green
    } else {
        Write-Host "  WARNING - No emails matched today" -ForegroundColor Yellow
    }
} else {
    Write-Host "  WARNING - No log file for today" -ForegroundColor Yellow
    Write-Host "  This means macro didn't receive any events today" -ForegroundColor Yellow
}

# Check 4: Input Files Freshness
Write-Host ""
Write-Host "[4/6] Checking input files freshness..." -ForegroundColor Yellow

$files = @(
    "input\Otchet po prirostu regiony\Po regionam.xlsx",
    "input\Otchet po prirostu aksessuarov po magazinam\Rassylka aksessuary magaziny.xlsx",
    "input\Obuv ostatki i oborachivaemost po gruppam tovara\Otchet po oborachivaemosti TZ region NNV.xlsx"
)

# Try alternate paths with Cyrillic
$alternateFiles = @(
    (Get-ChildItem (Join-Path $projectPath "input\*\*.xlsx") -Recurse | Where-Object { $_.Name -like "*регион*" } | Select-Object -First 1),
    (Get-ChildItem (Join-Path $projectPath "input\*\*.xlsx") -Recurse | Where-Object { $_.Name -like "*аксессуар*" } | Select-Object -First 1),
    (Get-ChildItem (Join-Path $projectPath "input\*\*.xlsx") -Recurse | Where-Object { $_.Name -like "*оборач*" } | Select-Object -First 1)
)

$allFresh = $true
$filesFound = 0

foreach ($file in $alternateFiles) {
    if ($file) {
        $filesFound++
        $fileInfo = $file
        $age = (Get-Date) - $fileInfo.LastWriteTime
        $ageHours = [math]::Round($age.TotalHours, 1)
        
        if ($age.TotalDays -lt 1) {
            Write-Host "  OK - $($fileInfo.Name) (${ageHours}h old)" -ForegroundColor Green
        } elseif ($age.TotalDays -lt 7) {
            Write-Host "  WARNING - $($fileInfo.Name) ($([math]::Round($age.TotalDays, 1))d old)" -ForegroundColor Yellow
            $allFresh = $false
        } else {
            Write-Host "  ERROR - $($fileInfo.Name) ($([math]::Round($age.TotalDays, 0))d old)" -ForegroundColor Red
            $allFresh = $false
        }
    }
}

Write-Host "  Found $filesFound out of 3 expected files" -ForegroundColor Cyan

# Check 5: Outlook Process
Write-Host ""
Write-Host "[5/6] Checking Outlook process..." -ForegroundColor Yellow
$outlook = Get-Process "OUTLOOK" -ErrorAction SilentlyContinue
if ($outlook) {
    Write-Host "  OK - Outlook is running" -ForegroundColor Green
    Write-Host "  Process started: $($outlook.StartTime)" -ForegroundColor Cyan
} else {
    Write-Host "  WARNING - Outlook is not running" -ForegroundColor Yellow
}

# Check 6: Generate Report
Write-Host ""
Write-Host "[6/6] Generating diagnostic report..." -ForegroundColor Yellow

$report = @"
========================================================
  KARI OUTLOOK MACRO - DIAGNOSTIC REPORT
========================================================
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

PROJECT STATUS
--------------
Project Path: $projectPath
Macro File: $(if (Test-Path $macroFile) { "OK" } else { "MISSING" })
Macro Version: $(if ((Get-Content $macroFile -Raw -Encoding UTF8) -match "GetSubjectSafe") { "v6.0" } else { "UNKNOWN" })

TODAY'S ACTIVITY
----------------
Date: $today
Log File: outlook_macro_$today.log
Status: $(if (Test-Path $logFile) { "EXISTS" } else { "NOT FOUND" })
$(if (Test-Path $logFile) {
    $logContent = Get-Content $logFile -Raw -Encoding UTF8
    $emailCount = ([regex]::Matches($logContent, "=== NEW EMAIL ===")).Count
    $matchCount = ([regex]::Matches($logContent, "MATCH: YES")).Count
    "Emails Processed: $emailCount
Emails Matched: $matchCount"
} else {
    "No activity today - macro didn't receive events"
})

INPUT FILES STATUS
------------------
Files found: $filesFound / 3
Status: $(if ($allFresh) { "ALL FRESH" } else { "SOME OLD" })

OUTLOOK PROCESS
---------------
Status: $(if ($outlook) { "RUNNING" } else { "NOT RUNNING" })
$(if ($outlook) { "Started: $($outlook.StartTime)" } else { "" })

DIAGNOSIS
---------
$(if (Test-Path $logFile) {
    $logContent = Get-Content $logFile -Raw -Encoding UTF8
    $matchCount = ([regex]::Matches($logContent, "MATCH: YES")).Count
    if ($matchCount -gt 0) {
        "STATUS: OK - Macro is working and catching emails"
    } else {
        "STATUS: WARNING - Macro is active but not matching emails
Possible causes:
  1. Email subjects don't match patterns
  2. Wrong macro version installed
  3. Test by forwarding an email to yourself"
    }
} else {
    "STATUS: ERROR - Macro is not receiving events
Possible causes:
  1. Macro not installed in ThisOutlookSession
  2. Macro security settings disabled
  3. Outlook needs restart
  
SOLUTION:
  1. Open Outlook
  2. Press Alt+F11 (VBA Editor)
  3. Check that code is in ThisOutlookSession
  4. Check that GetSubjectSafe function exists
  5. Restart Outlook completely"
})

NEXT STEPS
----------
1. If macro not working: Check VBA installation
2. If files old: Wait for Monday or save manually
3. Test by forwarding an email to yourself
4. Check new log entry after forwarding

========================================================
"@

$reportPath = Join-Path $projectPath "DIAGNOSTIC_REPORT.txt"
$report | Out-File -FilePath $reportPath -Encoding UTF8

Write-Host "  OK - Report saved: DIAGNOSTIC_REPORT.txt" -ForegroundColor Green

# Display Summary
Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "   DIAGNOSTIC SUMMARY" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if ($allFresh -and (Test-Path $logFile)) {
    $logContent = Get-Content $logFile -Raw -Encoding UTF8
    $matchCount = ([regex]::Matches($logContent, "MATCH: YES")).Count
    if ($matchCount -gt 0) {
        Write-Host "  STATUS: OK - System is working" -ForegroundColor Green
    } else {
        Write-Host "  STATUS: WARNING - Macro active but no matches" -ForegroundColor Yellow
    }
} elseif (-not (Test-Path $logFile)) {
    Write-Host "  STATUS: ERROR - Macro not receiving events" -ForegroundColor Red
} else {
    Write-Host "  STATUS: WARNING - Files are old" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Full report: DIAGNOSTIC_REPORT.txt" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Enter to open report..." -ForegroundColor Gray
Read-Host

notepad $reportPath
