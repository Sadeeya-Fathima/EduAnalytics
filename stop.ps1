
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$PidFile = Join-Path $ProjectRoot ".eduanalytics.pid"
$VenvPython = [IO.Path]::GetFullPath(
    (Join-Path $ProjectRoot ".venv\Scripts\python.exe")
)

try {
    # Stop every matching EduAnalytics Waitress process. This also repairs
    # stale or missing PID-file situations and prevents old templates being
    # served by a second copy of the application.
    $ManagedProcesses = @(
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object {
                $_.CommandLine -and
                $_.CommandLine -match '(?i)waitress' -and
                $_.CommandLine -match '(?i)--call\s+app:create_app' -and
                $_.CommandLine -match '(?i)--listen(?:=|\s+)0\.0\.0\.0:5000'
            }
    )

    foreach ($ManagedProcess in $ManagedProcesses) {
        Stop-Process -Id $ManagedProcess.ProcessId -Force -ErrorAction Stop
        Write-Host "Stopped EduAnalytics server process PID $($ManagedProcess.ProcessId)."
    }

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
        $CommandLine -notmatch '(?i)--listen(?:=|\s+)'
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
