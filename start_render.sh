#!/bin/bash

# Render startup script for PocketAgent

echo "Starting PocketAgent on Render..."

# Install Chrome for Render
apt-get update
apt-get install -y wget gnupg
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable xvfb

# Start Xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Start WPP Bridge in background
cd wpp-bridge
npm start &
WPP_PID=$!
cd ..

# Wait for WPP Bridge to start
sleep 5

# Start PocketAgent
python main_v2.py
