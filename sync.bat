@echo off
title Sentinel Auto-Deploy
color 0A

echo ============================================
echo   SENTINEL - Auto Deploy to Railway
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Staging all changes...
git add .
if %errorlevel% neq 0 (
    color 0C
    echo ERROR: git add failed!
    pause
    exit /b 1
)

:: Dynamic timestamp
for /f "tokens=1-5 delims=/ " %%a in ('date /t') do set DATE=%%a-%%b-%%c
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a:%%b

echo [2/3] Committing with timestamp...
git commit -m "Railway Auto-Deploy: %DATE% %TIME%"
if %errorlevel% neq 0 (
    echo No changes to commit. Already up to date.
)

echo [3/3] Pushing to GitHub (main)...
git push origin main
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERROR: Push failed! Check your internet connection or Git credentials.
    pause
    exit /b 1
)

echo.
echo ============================================
color 0B
echo    SUCCESS! Railway is now redeploying.
echo    Visit your Railway dashboard to monitor.
echo ============================================
echo.
timeout /t 3 >nul
