@echo off
REM CSReforge API Server Starter
echo ============================================
echo CSReforge API Server - Startup Script
echo ============================================
echo.

REM Change to the directory where the script is located
cd /d "%~dp0"

REM Check if logs directory exists
if not exist logs mkdir logs
echo Log directory checked...

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again.
    pause
    exit /b 1
)

echo Python installation found!

REM Check if the backend directory and main.py exist
if not exist backend\main.py (
    echo ERROR: backend\main.py not found
    echo Please make sure the project is properly installed.
    pause
    exit /b 1
)

echo Backend files found!
echo.
echo Starting CSReforge API server...

REM Start the server in a minimized window and redirect output to log file
start /min cmd /c "python backend\main.py > logs\api.log 2>&1"

echo.
echo CSReforge API server started in background.
echo Server logs are being written to: logs\api.log
echo.
echo To view logs in real-time, run: type logs\api.log
echo To stop the server, close the minimized command prompt window
echo or use Task Manager to end the Python process.
echo.
echo ============================================
echo      Server running at http://localhost:8000
echo ============================================
echo.

pause