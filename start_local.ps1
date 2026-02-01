# AI Employee Local Startup Script
# Run this to start everything locally on Windows

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting AI Employee Locally" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "[1/5] Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.11+" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "[2/5] Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Node.js $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check Python dependencies
Write-Host "[3/5] Checking Python dependencies..." -ForegroundColor Yellow
$composioInstalled = pip show composio-langchain 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
} else {
    Write-Host "✓ Python dependencies installed" -ForegroundColor Green
}

# Check Node.js dependencies
Write-Host "[4/5] Checking Node.js dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "wpp-bridge\node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Yellow
    Set-Location wpp-bridge
    npm install
    Set-Location ..
} else {
    Write-Host "✓ Node.js dependencies installed" -ForegroundColor Green
}

# Start WhatsApp Bridge in new window
Write-Host "[5/5] Starting WhatsApp Bridge..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\wpp-bridge'; Write-Host 'WhatsApp Bridge Starting...' -ForegroundColor Green; node index.js"

Write-Host "Waiting 5 seconds for WhatsApp Bridge to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Start AI Agent
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   AI Employee is Starting!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "WhatsApp Bridge: http://localhost:3001" -ForegroundColor Cyan
Write-Host "AI Agent: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Scan the QR code in the WhatsApp Bridge window!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start the main agent
python main_v2.py
