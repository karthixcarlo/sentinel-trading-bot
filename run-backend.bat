@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Creating venv with Python 3.10...
    py -3.10 -m venv .venv
    .venv\Scripts\python.exe -m ensurepip --upgrade
    .venv\Scripts\pip.exe install -r requirements.txt uvicorn fastapi
)
call .venv\Scripts\activate.bat
echo Starting Sentinel API on http://127.0.0.1:8000
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
pause
