# Project Sentinel – Local Setup

## Quick start (Windows)

### 1. Use the run scripts

**PowerShell:**
```powershell
.\run-backend.ps1
```

**Command Prompt:**
```cmd
run-backend.bat
```

### 2. If setup fails (MSYS2 Python / missing packages)

The backend needs **Windows Python 3.10** (from [python.org](https://www.python.org/downloads/)), because MSYS2/MinGW Python often fails to build numpy/pandas.

**Create a clean venv and install deps:**
```powershell
# Close any terminals using .venv first, then:
Remove-Item -Recurse -Force .venv -ErrorAction SilentlyContinue
py -3.10 -m venv .venv
.\.venv\Scripts\python.exe -m ensurepip --upgrade
.\.venv\Scripts\pip.exe install -r requirements.txt uvicorn fastapi
```

**Start the backend:**
```powershell
.\.venv\Scripts\activate
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend

```powershell
cd frontend
npm install
npm run dev
```

- Backend: http://127.0.0.1:8000  
- Frontend: http://localhost:5173  
