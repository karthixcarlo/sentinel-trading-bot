@echo off
echo ============================================
echo  PROJECT SENTINEL - Full Stack Launcher
echo ============================================

:: Kill any existing instances first
echo Clearing ports 5173 and 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
    taskkill /PID %%a /F >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do (
    taskkill /PID %%a /F >nul 2>&1
)

timeout /t 2 /nobreak >nul

echo.
echo [1/2] Starting FastAPI Backend on port 8000...
start "Sentinel Backend" cmd /k "cd /d C:\Users\Karthi\Desktop\Agent && C:\Users\Karthi\anaconda3\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak >nul

echo [2/2] Starting Vite Frontend on port 5173...
start "Sentinel Frontend" cmd /k "cd /d C:\Users\Karthi\Desktop\Agent\frontend && npm run dev"

timeout /t 5 /nobreak >nul

echo.
echo ============================================
echo  PROJECT SENTINEL IS RUNNING!
echo  Frontend : http://localhost:5173
echo  Backend  : http://localhost:8000
echo  API Docs : http://localhost:8000/docs
echo ============================================
echo.
start "" "http://localhost:5173/dashboard"
