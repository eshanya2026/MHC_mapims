# Troubleshooting Guide - MAPIMS Application

## ✅ Application Status Check

The application is currently **RUNNING** and accessible at:
- **Main Application**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin

## Common Issues and Solutions

### Issue 1: "Python was not found" or "Python is not recognized"

**Solution:**
1. Python 3.12.10 is installed, but you need to use `py -3` instead of `python`
2. Use the provided `run_app.bat` file to start the application
3. Or run manually: `py -3 app.py`

### Issue 2: "Port 5000 is already in use"

**Symptoms:**
- Error: "Address already in use"
- Cannot start the application

**Solution:**
1. Find the process using port 5000:
   ```powershell
   netstat -ano | findstr :5000
   ```
2. Stop the existing process:
   ```powershell
   taskkill /PID <process_id> /F
   ```
3. Or use a different port:
   ```powershell
   $env:PORT=5001
   py -3 app.py
   ```

### Issue 3: "Module not found" errors

**Solution:**
Install missing dependencies:
```powershell
py -3 -m pip install -r requirements.txt
```

### Issue 4: Cannot access http://localhost:5000 in browser

**Check:**
1. Is the application running?
   ```powershell
   netstat -ano | findstr :5000
   ```
2. Try accessing: http://127.0.0.1:5000
3. Check Windows Firewall settings
4. Check if another application is blocking the port

### Issue 5: MongoDB Connection Error

**Symptoms:**
- "ServerSelectionTimeoutError"
- "Connection refused"

**Solution:**
1. Check internet connection (MongoDB Atlas requires internet)
2. Verify MongoDB URI is correct in `.env` file or `app.py`
3. Check MongoDB Atlas IP whitelist settings

### Issue 6: OpenAI API Error

**Symptoms:**
- "Invalid API key"
- "Rate limit exceeded"

**Solution:**
1. Set `OPENAI_API_KEY` environment variable:
   ```powershell
   $env:OPENAI_API_KEY="your-api-key-here"
   ```
2. Or create a `.env` file with:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## How to Start the Application

### Method 1: Using the Batch File (Easiest)
Double-click `run_app.bat` or run:
```cmd
run_app.bat
```

### Method 2: Using PowerShell
```powershell
cd D:\Users\Public\APDCH_DM
py -3 app.py
```

### Method 3: With Environment Variables
```powershell
$env:FLASK_ENV="development"
$env:PORT=5000
py -3 app.py
```

## Verify Application is Running

1. **Check if process is running:**
   ```powershell
   Get-Process python -ErrorAction SilentlyContinue
   ```

2. **Check if port is listening:**
   ```powershell
   netstat -ano | findstr :5000
   ```

3. **Test the connection:**
   ```powershell
   Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing
   ```

## Stop the Application

1. **Find the process:**
   ```powershell
   Get-Process python | Select-Object Id, ProcessName
   ```

2. **Stop the process:**
   ```powershell
   Stop-Process -Id <process_id> -Force
   ```

3. **Or press Ctrl+C** in the terminal where it's running

## Quick Diagnostic Commands

Run these to check your setup:

```powershell
# Check Python version
py -3 --version

# Check if dependencies are installed
py -3 -m pip list | Select-String -Pattern "Flask|pymongo|openai"

# Check if application is running
netstat -ano | findstr :5000

# Test application response
Invoke-WebRequest -Uri "http://localhost:5000" -UseBasicParsing
```

## Still Having Issues?

1. Check the terminal/console output for error messages
2. Verify all files are in the correct location
3. Ensure you're in the correct directory: `D:\Users\Public\APDCH_DM`
4. Check Windows Event Viewer for system errors
5. Try running as Administrator

## Current Status

✅ Python 3.12.10 - Installed
✅ Dependencies - Installed
✅ Application - Running on port 5000
✅ Server Response - HTTP 200 OK

---

**Last Updated**: 2025-01-27
**Application Path**: D:\Users\Public\APDCH_DM

