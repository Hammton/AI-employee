@echo off
echo ========================================
echo   Starting AI Employee Locally
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.11 or higher
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Checking Python dependencies...
pip show composio-langchain >nul 2>&1
if errorlevel 1 (
    echo Installing Python dependencies...
    pip install -r requirements.txt
)

echo [2/4] Checking Node.js dependencies...
cd wpp-bridge
if not exist "node_modules" (
    echo Installing Node.js dependencies...
    npm install
)
cd ..

echo [3/4] Starting WhatsApp Bridge...
start "WhatsApp Bridge" cmd /k "cd wpp-bridge && node index.js"

echo Waiting 5 seconds for WhatsApp Bridge to start...
timeout /t 5 /nobreak >nul

echo [4/4] Starting AI Agent...
echo.
echo ========================================
echo   AI Employee is Starting!
echo ========================================
echo.
echo WhatsApp Bridge: http://localhost:3001
echo AI Agent: http://localhost:8000
echo.
echo IMPORTANT: Scan the QR code in the WhatsApp Bridge window!
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python main_v2.py
