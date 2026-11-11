@echo off
echo Stopping Flask app on port 5000...
echo.

REM Find and kill processes using port 5000
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5000 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a >nul 2>&1
)

REM Also kill any python.exe processes (be careful with this)
for /f "tokens=2" %%a in ('tasklist ^| findstr python.exe') do (
    echo Killing Python process %%a...
    taskkill /F /PID %%a >nul 2>&1
)

echo.
echo Done! Port 5000 should now be free.
echo.
pause

