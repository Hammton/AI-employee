#!/bin/bash

# Trace Kernel Deployment Script (VPS)
# Author: Pocket Agent Team
# Description: One-click setup for Ubuntu 22.04+

set -e  # Exit on error

echo "🚀 Initializing Trace Kernel Deployment..."
echo "----------------------------------------"

# 1. System Updates
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get install -y python3.10-venv python3-pip nodejs npm git

# 2. Node.js Update (ensure v18+)
echo "📦 Ensuring Node.js LTS..."
sudo npm install -g n
sudo n lts

# 3. Environment Setup
echo "⚙️ Configuring Environment..."
if [ ! -f .env ]; then
    echo "Creating .env from example..."
    cp .env.example .env
fi

# 4. Interactive Configuration
echo "----------------------------------------"
echo "🔑 CREDENTIAL SETUP (Press Enter to keep existing/default)"

read -p "Enter OpenRouter API Key: " OR_KEY
if [ ! -z "$OR_KEY" ]; then
    sed -i "s|OPENROUTER_API_KEY=.*|OPENROUTER_API_KEY=$OR_KEY|g" .env
fi

read -p "Enter Composio API Key: " COMP_KEY
if [ ! -z "$COMP_KEY" ]; then
    sed -i "s|COMPOSIO_API_KEY=.*|COMPOSIO_API_KEY=$COMP_KEY|g" .env
fi

# 5. Application Installation
echo "snake Installing Python Dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "🌐 Installing WPP Bridge..."
cd wpp-bridge
npm install
cd ..

# 6. Systemd Service Setup
echo "running Installing Systemd Service (Auto-Start)..."

SERVICE_FILE="/etc/systemd/system/pocketagent.service"
CURRENT_DIR=$(pwd)

sudo bash -c "cat > $SERVICE_FILE" <<EOF
[Unit]
Description=Pocket Agent Trace Kernel
After=network.target

[Service]
User=root
WorkingDirectory=$CURRENT_DIR
ExecStart=/bin/bash -c 'source $CURRENT_DIR/venv/bin/activate && python main_v2.py'
Restart=always
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

# Note: We don't auto-start WPP Bridge in systemd because it requires manual QR scan initially.
# We'll run it once interactively or let the user run it.

echo "✅ Service configured."
sudo systemctl daemon-reload
sudo systemctl enable pocketagent

# 7. Final Instructions
echo "----------------------------------------"
echo "🎉 DEPLOYMENT COMPLETE!"
echo "----------------------------------------"
echo "To finish setup:"
echo "1. Start the WhatsApp Bridge to scan QR code:"
echo "   cd wpp-bridge && node index.js"
echo ""
echo "2. Once connected, start the Agent Kernel:"
echo "   sudo systemctl start pocketagent"
echo ""
echo "3. Monitor logs:"
echo "   journalctl -u pocketagent -f"
echo "----------------------------------------"
