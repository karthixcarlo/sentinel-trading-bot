# Project Sentinel - Start FastAPI Backend
# Uses .venv with Python 3.10 (Windows) for numpy/pandas compatibility

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating venv with Python 3.10..." -ForegroundColor Yellow
    py -3.10 -m venv .venv
    .\.venv\Scripts\python.exe -m ensurepip --upgrade
    .\.venv\Scripts\pip.exe install -r requirements.txt uvicorn fastapi
}

.\.venv\Scripts\activate.ps1
Write-Host "Starting Sentinel API on http://127.0.0.1:8000" -ForegroundColor Green
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
