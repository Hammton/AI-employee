#!/bin/bash

echo "========================================"
echo "  Starting AI Employee Locally"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.11 or higher"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "[1/4] Checking Python dependencies..."
if ! pip show composio-langchain &> /dev/null; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

echo "[2/4] Checking Node.js dependencies..."
cd wpp-bridge
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi
cd ..

echo "[3/4] Starting WhatsApp Bridge..."
cd wpp-bridge
node index.js &
WPP_PID=$!
cd ..

echo "Waiting 5 seconds for WhatsApp Bridge to start..."
sleep 5

echo "[4/4] Starting AI Agent..."
echo ""
echo "========================================"
echo "  AI Employee is Starting!"
echo "========================================"
echo ""
echo "WhatsApp Bridge: http://localhost:3001"
echo "AI Agent: http://localhost:8000"
echo ""
echo "IMPORTANT: Scan the QR code in the WhatsApp Bridge window!"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"
echo ""

# Trap Ctrl+C to kill both processes
trap "kill $WPP_PID; exit" INT

python3 main.py
