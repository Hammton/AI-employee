#!/bin/bash

# Railway startup script for PocketAgent

echo "Starting PocketAgent on Railway..."

# Start WPP Bridge in background
cd wpp-bridge
npm start &
WPP_PID=$!
cd ..

# Wait for WPP Bridge to start
sleep 5

# Start PocketAgent
python main_v2.py &
AGENT_PID=$!

# Keep script running
wait $AGENT_PID
