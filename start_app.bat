@echo off
echo ========================================
echo   MAPIMS Health Assessment System
echo   Starting Application...
echo ========================================
echo.

REM Set development environment
set FLASK_ENV=development

REM Run the application
py -3 app.py

pause

