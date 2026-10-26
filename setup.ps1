
$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "       EduAnalytics Setup Check       " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check Python 3.12
try {
    $pythonVersion = & python --version 2>&1

    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed"
    }

    if ($pythonVersion -notmatch '^Python 3\.12(\.\d+)?$') {
        Write-Host "[ERROR] Python 3.12 is required. Detected: $pythonVersion" -ForegroundColor Red
        Write-Host "Install Python 3.12 and enable Add Python to PATH." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Python 3.12 was not found. Install Python 3.12 and enable Add Python to PATH." -ForegroundColor Red
    exit 1
}

# Check Git
try {
    $gitVersion = & git --version 2>&1

    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed"
    }

    Write-Host "[OK] $gitVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Git was not found. Install Git for Windows." -ForegroundColor Red
    exit 1
}

# Verify the EduAnalytics project root
if (
    -not (Test-Path ".\requirements.txt" -PathType Leaf) -or
    -not (Test-Path ".\app\__init__.py" -PathType Leaf) -or
    -not (Test-Path ".\app\models.py" -PathType Leaf)
) {
    Write-Host "[ERROR] Run this script from the EduAnalytics project root. Required project files were not found." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] EduAnalytics project files found" -ForegroundColor Green

# Create or reuse the virtual environment
if (Test-Path ".\.venv\Scripts\python.exe" -PathType Leaf) {
    Write-Host "[OK] Existing virtual environment found; reusing it." -ForegroundColor Green
}
else {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan

    & python -m venv .venv

    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Could not create the virtual environment." -ForegroundColor Red
        exit 1
    }

    if (-not (Test-Path ".\.venv\Scripts\python.exe" -PathType Leaf)) {
        Write-Host "[ERROR] Virtual environment creation did not produce the expected Python executable." -ForegroundColor Red
        exit 1
    }

    Write-Host "[OK] Virtual environment created." -ForegroundColor Green
}

# Install dependencies using the virtual environment's Python
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan

& ".\.venv\Scripts\python.exe" -m pip install -r .\requirements.txt

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Dependency installation failed. Check the error above and rerun setup.ps1." -ForegroundColor Red
    exit 1
}

Write-Host "[OK] Dependencies installed or already satisfied." -ForegroundColor Green
Write-Host ""

# Preserve or create a persistent SECRET_KEY
$secretKey = [Environment]::GetEnvironmentVariable("SECRET_KEY", "User")

if ([string]::IsNullOrWhiteSpace($secretKey)) {
    Write-Host "Generating a persistent SECRET_KEY..." -ForegroundColor Cyan

    $secretKey = & ".\.venv\Scripts\python.exe" -c "import secrets; print(secrets.token_hex(32))"

    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($secretKey)) {
        Write-Host "[ERROR] Could not generate SECRET_KEY." -ForegroundColor Red
        exit 1
    }

    $secretKey = $secretKey.Trim()

    try {
        [Environment]::SetEnvironmentVariable("SECRET_KEY", $secretKey, "User")
        Write-Host "[OK] A persistent SECRET_KEY was created." -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR] Could not save SECRET_KEY to the Windows user environment." -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "[OK] Existing persistent SECRET_KEY preserved." -ForegroundColor Green
}

# Make the key available to this PowerShell session
$env:SECRET_KEY = $secretKey
Remove-Variable secretKey

Write-Host ""
Write-Host "Setup dependencies and secret-key configuration completed." -ForegroundColor Green
Write-Host "Existing database contents were not changed."
