@echo off
echo ========================================
echo     PocketAgent - Startup Script
echo ========================================
echo.
echo Starting WPP Bridge (Node.js)...
start "WPP Bridge" cmd /k "cd wpp-bridge && npm start"
echo.
echo Waiting for WPP Bridge to start...
timeout /t 5 /nobreak >nul
echo.
echo Starting PocketAgent (Python)...
python main_v2.py
