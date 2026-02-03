@echo off
REM Sentinel Hive - Autonomous Trading System Launcher
REM Runs the multi-agent system 24/7

echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║       SENTINEL HIVE - Autonomous Trading System          ║
echo ║                   Startup Script                          ║
echo ║                                                          ║
╚══════════════════════════════════════════════════════════╝

echo.
echo [1/3] Checking virtual environment...
if not exist ".venv\" (
    echo ❌ Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo ✅ Virtual environment found
echo.

echo [2/3] Activating environment...
call .venv\Scripts\activate.bat
echo ✅ Environment activated
echo.

echo [3/3] Starting Sentinel Hive...
echo.
echo ⚠️  Press Ctrl+C to stop the autonomous system
echo.

python run_autonomous.py

echo.
echo 👋 Sentinel Hive stopped
pause
