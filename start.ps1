
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot

$ListenHost = [Environment]::GetEnvironmentVariable(
    "EDUANALYTICS_HOST",
    "Process"
)

if ([string]::IsNullOrWhiteSpace($ListenHost)) {
    $ListenHost = "127.0.0.1"
}

$ListenPort = 5000
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$PidFile = Join-Path $ProjectRoot ".eduanalytics.pid"
$LogFile = Join-Path $ProjectRoot "eduanalytics.log"
$ErrorLogFile = Join-Path $ProjectRoot "eduanalytics.log.err"

# Determine whether first-run setup is complete by checking /setup/.
# Expected behavior: HTTP 200 means setup is available; HTTP 403
# means setup has already been completed.
function Get-SetupDestination {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl
    )

    try {
        $Response = Invoke-WebRequest `
            -Uri "$BaseUrl/setup/" `
            -TimeoutSec 5 `
            -UseBasicParsing `
            -ErrorAction Stop

        if ([int]$Response.StatusCode -eq 200) {
            return "setup"
        }

        throw "Unexpected HTTP status $([int]$Response.StatusCode) from the setup page."
    }
    catch {
        $StatusCode = $null

        if ($_.Exception.Response -and $_.Exception.Response.StatusCode) {
            $StatusCode = [int]$_.Exception.Response.StatusCode
        }

        if ($StatusCode -eq 403) {
            return "login"
        }

        throw "Could not determine setup status at $BaseUrl/setup/. $($_.Exception.Message)"
    }
}

# Display the appropriate next page without guessing if the check fails.
function Show-NextPage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$BaseUrl
    )

    try {
        $Destination = Get-SetupDestination -BaseUrl $BaseUrl

        if ($Destination -eq "setup") {
            Write-Host ""
            Write-Host "First-run setup is not complete." -ForegroundColor Yellow
            Write-Host "Register your institution and create the initial Administrator:"
            Write-Host "$BaseUrl/setup/" -ForegroundColor Cyan
        }
        else {
            Write-Host ""
            Write-Host "EduAnalytics is already configured." -ForegroundColor Green
            Write-Host "Open this page to sign in:"
            Write-Host "$BaseUrl/auth/login" -ForegroundColor Cyan
        }
    }
    catch {
        Write-Host ""
        Write-Host "[WARNING] The server is running, but setup status could not be determined." -ForegroundColor Yellow
        Write-Host "Open $BaseUrl/ and check eduanalytics.log.err if necessary."
        Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

try {
    Set-Location $ProjectRoot

    # 1. Verify the virtual environment exists.
    if (-not (Test-Path $VenvPython -PathType Leaf)) {
        throw "Virtual environment not found. Run .\setup.ps1 first."
    }

    # 2. Load the existing persistent SECRET_KEY.
    $SecretKey = [Environment]::GetEnvironmentVariable(
        "SECRET_KEY",
        "Process"
    )

    if ([string]::IsNullOrWhiteSpace($SecretKey)) {
        $SecretKey = [Environment]::GetEnvironmentVariable(
            "SECRET_KEY",
            "User"
        )
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
                    Write-Host "EduAnalytics is already running (PID $ExistingPid)." -ForegroundColor Yellow

                    Show-NextPage -BaseUrl "http://127.0.0.1:$ListenPort"

                    if ($ListenHost -eq "0.0.0.0") {
                        Write-Host ""
                        Write-Host "The server may also be accessible from authorized devices on your LAN."
                        Write-Host "Use the host PC's private IP address and port $ListenPort."
                    }

                    Write-Host ""
                    Write-Host "To stop: .\stop.ps1"
                    return
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
    $Process = Start-Process `
        -FilePath $VenvPython `
        -ArgumentList @(
            "-m",
            "waitress",
            "--listen=${ListenHost}:${ListenPort}",
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
            -Uri "http://127.0.0.1:$ListenPort/" `
            -TimeoutSec 5 `
            -UseBasicParsing `
            -ErrorAction Stop

        Write-Host "EduAnalytics started successfully." -ForegroundColor Green
        Write-Host "Local URL: http://127.0.0.1:$ListenPort/"
        Write-Host "Listening host: $ListenHost"
        Write-Host "HTTP status: $([int]$Response.StatusCode)"

        # Display the correct setup or login destination.
        Show-NextPage -BaseUrl "http://127.0.0.1:$ListenPort"

        # 8. Display LAN URLs when LAN binding is enabled.
        if ($ListenHost -eq "0.0.0.0") {
            $LanAddresses = @()

            try {
                $LanAddresses = @(
                    Get-NetIPConfiguration -ErrorAction Stop |
                        Where-Object {
                            $_.IPv4DefaultGateway -ne $null -and
                            $_.NetAdapter.Status -eq "Up"
                        } |
                        ForEach-Object {
                            $_.IPv4Address.IPAddress
                        } |
                        Where-Object {
                            $_ -and
                            $_ -notmatch '^127\.' -and
                            $_ -notmatch '^169\.254\.'
                        } |
                        Sort-Object -Unique
                )
            }
            catch {
                Write-Host "Could not automatically detect LAN addresses. Find them with Get-NetIPConfiguration." -ForegroundColor Yellow
            }

            if ($LanAddresses.Count -gt 0) {
                Write-Host ""
                Write-Host "LAN URL(s):" -ForegroundColor Cyan

                foreach ($Address in $LanAddresses) {
                    $LanBaseUrl = "http://${Address}:$ListenPort"

                    Write-Host "$LanBaseUrl/"

                    # Also display the correct page for LAN users.
                    Show-NextPage -BaseUrl $LanBaseUrl
                }
            }
            else {
                Write-Host "LAN address not detected. Find it with Get-NetIPConfiguration." -ForegroundColor Yellow
            }
        }
        elseif ($ListenHost -notin @("127.0.0.1", "localhost")) {
            Write-Host "Configured host URL: http://${ListenHost}:$ListenPort/"
        }
    }
    catch {
        # A running process does not guarantee that HTTP is responding.
        Write-Host "Waitress is running (PID $($Process.Id)), but the homepage check did not return a response." -ForegroundColor Yellow
        Write-Host "Review eduanalytics.log and eduanalytics.log.err if the app is inaccessible."
    }

    Write-Host ""
    Write-Host "To stop: .\stop.ps1"
}
catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}
