
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PidFile = Join-Path $ProjectRoot ".eduanalytics.pid"
$LogFile = Join-Path $ProjectRoot "eduanalytics.log"
$ErrorLogFile = Join-Path $ProjectRoot "eduanalytics.log.err"

try {
    Set-Location $ProjectRoot

    # 1. Verify the virtual environment exists.
    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        throw "Virtual environment not found. Run .\setup.ps1 first."
    }

    # 2. Load the existing persistent SECRET_KEY.
    $SecretKey = [Environment]::GetEnvironmentVariable("SECRET_KEY", "Process")

    if ([string]::IsNullOrWhiteSpace($SecretKey)) {
        $SecretKey = [Environment]::GetEnvironmentVariable("SECRET_KEY", "User")
    }

    if ([string]::IsNullOrWhiteSpace($SecretKey)) {
        throw "SECRET_KEY is missing. Run .\setup.ps1 to configure it."
    }

    $env:SECRET_KEY = $SecretKey
    Remove-Variable SecretKey

    # 3. Check whether the PID file points to an existing process.
    if (Test-Path $PidFile) {
        $ExistingPid = (Get-Content $PidFile -Raw).Trim()

        if ($ExistingPid -match '^\d+$') {
            $ExistingProcess = Get-CimInstance Win32_Process `
                -Filter "ProcessId = $ExistingPid" `
                -ErrorAction SilentlyContinue

            if ($ExistingProcess) {
                $ExpectedPython = [IO.Path]::GetFullPath($VenvPython)

                if (
                    $ExistingProcess.ExecutablePath -eq $ExpectedPython -and
                    $ExistingProcess.CommandLine -match 'waitress'
                ) {
                    throw "EduAnalytics is already running (PID $ExistingPid). Use .\stop.ps1 before restarting."
                }

                throw "PID file points to another process. Nothing was stopped. Inspect .eduanalytics.pid before continuing."
            }
        }
        else {
            throw "PID file is invalid. Inspect .eduanalytics.pid before continuing."
        }

        # The recorded process no longer exists; remove the stale PID file.
        Remove-Item $PidFile -Force
    }

    # 4. Verify Waitress is installed.
    & $VenvPython -m waitress --help *> $null

    if ($LASTEXITCODE -ne 0) {
        throw "Waitress is unavailable. Run .\setup.ps1 to install dependencies."
    }

    # 5. Clear old logs for this startup attempt.
    Remove-Item $LogFile, $ErrorLogFile -Force -ErrorAction SilentlyContinue

    # 6. Start the Flask application through Waitress.
    # Bind to localhost for Phase 4; LAN access can be configured in Phase 5.
    $Process = Start-Process `
        -FilePath $VenvPython `
        -ArgumentList @(
            "-m",
            "waitress",
            "--listen=127.0.0.1:5000",
            "--call",
            "app:create_app"
        ) `
        -WorkingDirectory $ProjectRoot `
        -RedirectStandardOutput $LogFile `
        -RedirectStandardError $ErrorLogFile `
        -PassThru `
        -WindowStyle Hidden

    # 7. Record the PID, then verify the process and HTTP response.
    Set-Content -Path $PidFile -Value $Process.Id

    Start-Sleep -Seconds 2
    $Process.Refresh()

    if ($Process.HasExited) {
        Remove-Item $PidFile -Force -ErrorAction SilentlyContinue
        throw "EduAnalytics failed to start. Review eduanalytics.log and eduanalytics.log.err."
    }

    try {
        $Response = Invoke-WebRequest `
            -Uri "http://127.0.0.1:5000/" `
            -TimeoutSec 5 `
            -UseBasicParsing `
            -ErrorAction Stop

        Write-Host "EduAnalytics started successfully." -ForegroundColor Green
        Write-Host "Local URL: http://127.0.0.1:5000"
        Write-Host "HTTP status: $([int]$Response.StatusCode)"
    }
    catch {
        # The root route may redirect or require setup/login.
        # A running process is not necessarily a failed startup.
        Write-Host "Waitress is running (PID $($Process.Id)), but the homepage check did not return a response." -ForegroundColor Yellow
        Write-Host "Review eduanalytics.log and eduanalytics.log.err if the app is inaccessible."
    }

    Write-Host "To stop: .\stop.ps1"
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
