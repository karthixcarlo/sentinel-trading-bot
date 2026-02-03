@echo off
REM Launch Project Sentinel Dashboard
echo ========================================
echo   Project Sentinel - Dashboard Launcher
echo ========================================
echo.

REM Check if virtual environment exists
if not exist .venv\ (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Installing dashboard dependencies...
pip install --quiet streamlit plotly streamlit-option-menu

echo.
echo ========================================
echo   Starting Dashboard...
echo   Opening browser at: http://localhost:8501
echo ========================================
echo.
echo Press Ctrl+C to stop the dashboard
echo.

REM Launch Streamlit
streamlit run dashboard.py --server.port 8501 --server.headless false

pause
