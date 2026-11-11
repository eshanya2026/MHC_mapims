@echo off
echo ========================================
echo   Installing MAPIMS Dependencies
echo ========================================
echo.

REM Try using py launcher first
echo Attempting installation with py -3...
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements.txt

REM Verify installation
echo.
echo Verifying installation...
py -3 -c "import openai, flask, pymongo; print('SUCCESS: All modules installed!')" 2>nul
if %errorlevel% neq 0 (
    echo.
    echo Installation may have failed. Trying alternative method...
    .\Scripts\pip.exe install -r requirements.txt
    echo.
    echo Please verify by running: py -3 -c "import openai"
)

echo.
echo ========================================
echo   Installation Complete
echo ========================================
pause

