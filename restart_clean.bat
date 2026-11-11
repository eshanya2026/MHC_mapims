@echo off
echo ========================================
echo   MAPIMS - Clean Restart (No Cache)
echo ========================================
echo.

REM Stop any running Flask processes
echo [1/5] Stopping existing Flask processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo   Killing process on port 5000: %%a
    taskkill /F /PID %%a >nul 2>&1
)

REM Kill Python processes
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM pythonw.exe /T >nul 2>&1
timeout /t 2 >nul

REM Clear Python cache
echo [2/5] Clearing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d" 2>nul
del /s /q *.pyc 2>nul
echo   Python cache cleared

REM Clear Flask session files (if any)
echo [3/5] Clearing Flask session files...
if exist "flask_session" rd /s /q "flask_session" 2>nul
if exist ".flask_session" rd /s /q ".flask_session" 2>nul
echo   Session files cleared

REM Clear any .env cache (if exists)
echo [4/5] Checking environment...
if exist ".env.bak" del /q ".env.bak" 2>nul

REM Set environment to clear cache
echo [5/5] Setting environment variables...
set FLASK_ENV=development
set PYTHONDONTWRITEBYTECODE=1
set FLASK_DEBUG=1

echo.
echo ========================================
echo   Starting Flask Application...
echo ========================================
echo.
echo   Server will start at: http://localhost:5000
echo   Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the application
py -3 app.py

pause
