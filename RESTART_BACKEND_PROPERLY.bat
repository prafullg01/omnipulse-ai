@echo off
echo ============================================
echo OMNIPULSE AI - Clean Backend Restart
echo ============================================
echo.

echo Step 1: Killing all existing Python processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo Killing process ID: %%a
    taskkill /F /PID %%a 2>nul
)

echo.
echo Step 2: Waiting 2 seconds for cleanup...
timeout /t 2 /nobreak >nul

echo.
echo Step 3: Starting fresh backend server...
cd backend
start "OMNIPULSE Backend" cmd /k "python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo Step 4: Waiting 3 seconds for server to start...
timeout /t 3 /nobreak >nul

echo.
echo Step 5: Verifying server is responding...
curl http://localhost:8000/api/analytics/roi -UseBasicParsing 2>nul | findstr "total_revenue"

echo.
echo ============================================
echo Backend restarted successfully!
echo ============================================
echo.
echo Now refresh your browser with: Ctrl+Shift+R
echo.
pause
