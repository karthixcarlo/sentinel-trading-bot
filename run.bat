@echo off
REM Run script for Project Sentinel examples and tests
REM This ensures the correct Python environment is used

echo ============================================================
echo Project Sentinel - Phase 1
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please create it with: python -m venv .venv
    echo Then activate it and run: pip install -e .
    exit /b 1
)

REM Run based on argument
if "%1"=="test" (
    echo Running all tests...
    echo.
    .venv\Scripts\python.exe -m pytest tests/ -v
) else if "%1"=="examples" (
    echo Running Phase 1 examples...
    echo.
    .venv\Scripts\python.exe examples/phase1_examples.py
) else if "%1"=="test-quick" (
    echo Running quick test...
    echo.
    .venv\Scripts\python.exe -m pytest tests/ -q
) else (
    echo Usage: run.bat [command]
    echo.
    echo Commands:
    echo   test         - Run all tests with verbose output
    echo   test-quick   - Run all tests with minimal output
    echo   examples     - Run Phase 1 example demonstrations
    echo.
    echo Example: run.bat test
)

echo.
echo ============================================================
