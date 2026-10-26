
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$PidFile = Join-Path $ProjectRoot ".eduanalytics.pid"
$VenvPython = [IO.Path]::GetFullPath(
    (Join-Path $ProjectRoot ".venv\Scripts\python.exe")
)

try {
    # 1. Check for the PID file.
    if (-not (Test-Path $PidFile -PathType Leaf)) {
        Write-Host "EduAnalytics is not running (PID file not found)." -ForegroundColor Yellow
        exit 0
    }

    $StoredPid = (Get-Content $PidFile -Raw).Trim()

    if ($StoredPid -notmatch '^\d+$') {
        throw "PID file is invalid. Inspect .eduanalytics.pid. No process was stopped."
    }

    $TargetPid = [int]$StoredPid

    # 2. Look up the exact process recorded in the PID file.
    $ServerProcess = Get-CimInstance Win32_Process `
        -Filter "ProcessId = $TargetPid" `
        -ErrorAction SilentlyContinue

    if (-not $ServerProcess) {
        Remove-Item $PidFile -Force
        Write-Host "Removed stale PID file; EduAnalytics was not running." -ForegroundColor Yellow
        exit 0
    }

    # 3. Verify this is the project's Waitress server.
    $CommandLine = [string]$ServerProcess.CommandLine

    if (
        $ServerProcess.ExecutablePath -ne $VenvPython -or
        $CommandLine -notmatch '(?i)waitress' -or
        $CommandLine -notmatch '(?i)app:create_app' -or
        $CommandLine -notmatch '(?i)127\.0\.0\.1:5000'
    ) {
        throw "Recorded PID does not match the expected EduAnalytics server. Nothing was stopped. Inspect .eduanalytics.pid."
    }

    # 4. Stop only the verified server process.
    Stop-Process -Id $TargetPid -Force -ErrorAction Stop

    # 5. Wait briefly for the process to exit.
    $Deadline = (Get-Date).AddSeconds(10)

    do {
        Start-Sleep -Milliseconds 250

        $RemainingProcess = Get-CimInstance Win32_Process `
            -Filter "ProcessId = $TargetPid" `
            -ErrorAction SilentlyContinue

        if (-not $RemainingProcess) {
            break
        }
    } while ((Get-Date) -lt $Deadline)

    if ($RemainingProcess) {
        throw "The server process has not exited. PID file retained for investigation."
    }

    # 6. Remove the PID file after confirmed shutdown.
    Remove-Item $PidFile -Force -ErrorAction SilentlyContinue

    Write-Host "EduAnalytics has been stopped successfully." -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
