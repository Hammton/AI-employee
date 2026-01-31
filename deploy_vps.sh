#!/bin/bash

# PocketAgent VPS Deployment Script
# This script automates the deployment of PocketAgent on a fresh Ubuntu 22.04 VPS

set -e  # Exit on error

echo "========================================="
echo "  PocketAgent VPS Deployment Script"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Running as root"

# Update system
echo ""
echo "Step 1: Updating system..."
apt update && apt upgrade -y
echo -e "${GREEN}✓${NC} System updated"

# Install Python 3.11
echo ""
echo "Step 2: Installing Python 3.11..."
apt install -y python3.11 python3.11-venv python3-pip
echo -e "${GREEN}✓${NC} Python 3.11 installed"

# Install Node.js 18+
echo ""
echo "Step 3: Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
echo -e "${GREEN}✓${NC} Node.js installed ($(node --version))"

# Install Chrome
echo ""
echo "Step 4: Installing Google Chrome..."
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb
echo -e "${GREEN}✓${NC} Chrome installed"

# Install Xvfb (for headless Chrome)
echo ""
echo "Step 5: Installing Xvfb..."
apt install -y xvfb
echo -e "${GREEN}✓${NC} Xvfb installed"

# Install Git
echo ""
echo "Step 6: Installing Git..."
apt install -y git
echo -e "${GREEN}✓${NC} Git installed"

# Clone repository
echo ""
echo "Step 7: Cloning PocketAgent repository..."
read -p "Enter your GitHub repository URL: " REPO_URL
cd /root
if [ -d "pocket-agent" ]; then
    echo -e "${YELLOW}⚠${NC} pocket-agent directory already exists. Skipping clone."
else
    git clone "$REPO_URL" pocket-agent
    echo -e "${GREEN}✓${NC} Repository cloned"
fi

cd /root/pocket-agent

# Create Python virtual environment
echo ""
echo "Step 8: Setting up Python environment..."
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Python environment ready"

# Install Node dependencies
echo ""
echo "Step 9: Installing Node.js dependencies..."
cd wpp-bridge
npm install
cd ..
echo -e "${GREEN}✓${NC} Node.js dependencies installed"

# Configure environment
echo ""
echo "Step 10: Configuring environment..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠${NC} .env file already exists. Skipping."
else
    echo "Creating .env file..."
    read -p "Enter OPENROUTER_API_KEY: " OPENROUTER_KEY
    read -p "Enter COMPOSIO_API_KEY: " COMPOSIO_KEY
    read -p "Enter MEM0_API_KEY: " MEM0_KEY
    read -p "Enter USER_PHONE (e.g., +1234567890): " USER_PHONE
    
    cat > .env << EOF
# Required API Keys
OPENROUTER_API_KEY=$OPENROUTER_KEY
COMPOSIO_API_KEY=$COMPOSIO_KEY
MEM0_API_KEY=$MEM0_KEY

# Server Configuration
PORT=8000
WPP_BRIDGE_URL=http://localhost:3001
WPP_BRIDGE_PORT=3001

# AI Models
LLM_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
IMAGE_MODEL=google/gemini-2.5-flash-image
AUDIO_MODEL=google/gemini-3-flash-preview
TTS_MODEL=google/gemini-3-flash-preview

# WhatsApp
USER_PHONE=$USER_PHONE
WPP_SESSION_NAME=pocket-agent
WPP_HEADLESS=true

# Autonomous Execution
AUTONOMOUS_EXECUTION_APPROVAL=true
EOF
    echo -e "${GREEN}✓${NC} .env file created"
fi

# Create systemd services
echo ""
echo "Step 11: Creating systemd services..."

# Xvfb service
cat > /etc/systemd/system/xvfb.service << 'EOF'
[Unit]
Description=X Virtual Frame Buffer Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x24
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# WPP Bridge service
cat > /etc/systemd/system/wpp-bridge.service << 'EOF'
[Unit]
Description=WPP Bridge for WhatsApp
After=network.target xvfb.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/pocket-agent/wpp-bridge
ExecStart=/usr/bin/node index.js
Restart=always
RestartSec=10
Environment="DISPLAY=:99"

[Install]
WantedBy=multi-user.target
EOF

# PocketAgent service
cat > /etc/systemd/system/pocketagent.service << 'EOF'
[Unit]
Description=PocketAgent AI Assistant
After=network.target wpp-bridge.service

[Service]
Type=simple
User=root
WorkingDirectory=/root/pocket-agent
Environment="PATH=/root/pocket-agent/venv/bin"
ExecStart=/root/pocket-agent/venv/bin/python main_v2.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓${NC} Systemd services created"

# Reload systemd
systemctl daemon-reload

# Enable services
echo ""
echo "Step 12: Enabling services..."
systemctl enable xvfb
systemctl enable wpp-bridge
systemctl enable pocketagent
echo -e "${GREEN}✓${NC} Services enabled"

# Create backup script
echo ""
echo "Step 13: Creating backup script..."
mkdir -p /root/backups

cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /root/backups/pocket-agent-$DATE.tar.gz \
  /root/pocket-agent/.env \
  /root/pocket-agent/wpp-bridge/tokens \
  /root/pocket-agent/memory

# Keep only last 7 backups
find /root/backups -name "pocket-agent-*.tar.gz" -mtime +7 -delete
EOF

chmod +x /root/backup.sh
echo -e "${GREEN}✓${NC} Backup script created"

# Create health check script
echo ""
echo "Step 14: Creating health check script..."
cat > /root/health-check.sh << 'EOF'
#!/bin/bash

# Check if services are running
if ! systemctl is-active --quiet pocketagent; then
    echo "PocketAgent is down! Restarting..."
    systemctl restart pocketagent
fi

if ! systemctl is-active --quiet wpp-bridge; then
    echo "WPP Bridge is down! Restarting..."
    systemctl restart wpp-bridge
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Warning: Disk usage is at ${DISK_USAGE}%"
fi

# Check memory
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}' | cut -d. -f1)
if [ $MEM_USAGE -gt 80 ]; then
    echo "Warning: Memory usage is at ${MEM_USAGE}%"
fi
EOF

chmod +x /root/health-check.sh
echo -e "${GREEN}✓${NC} Health check script created"

# Setup cron jobs
echo ""
echo "Step 15: Setting up cron jobs..."
(crontab -l 2>/dev/null; echo "0 3 * * * /root/backup.sh") | crontab -
(crontab -l 2>/dev/null; echo "*/5 * * * * /root/health-check.sh") | crontab -
echo -e "${GREEN}✓${NC} Cron jobs configured"

# Setup firewall
echo ""
echo "Step 16: Configuring firewall..."
apt install -y ufw
ufw --force enable
ufw allow 22
echo -e "${GREEN}✓${NC} Firewall configured"

# Start services
echo ""
echo "Step 17: Starting services..."
systemctl start xvfb
sleep 2
systemctl start wpp-bridge
sleep 2
systemctl start pocketagent
echo -e "${GREEN}✓${NC} Services started"

# Final instructions
echo ""
echo "========================================="
echo "  Deployment Complete! ✅"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Connect WhatsApp:"
echo "   - Stop WPP Bridge: systemctl stop wpp-bridge"
echo "   - Run manually: cd /root/pocket-agent/wpp-bridge && DISPLAY=:99 node index.js"
echo "   - Scan QR code with your phone"
echo "   - Press Ctrl+C after connected"
echo "   - Start service: systemctl start wpp-bridge"
echo ""
echo "2. Check status:"
echo "   systemctl status pocketagent"
echo "   systemctl status wpp-bridge"
echo ""
echo "3. View logs:"
echo "   journalctl -u pocketagent -f"
echo "   journalctl -u wpp-bridge -f"
echo ""
echo "4. Test health:"
echo "   curl http://localhost:8000/health"
echo ""
echo "5. Send a WhatsApp message to test!"
echo ""
echo "========================================="
echo "  Useful Commands"
echo "========================================="
echo ""
echo "Restart services:    systemctl restart pocketagent wpp-bridge"
echo "View logs:           journalctl -u pocketagent -f"
echo "Backup:              /root/backup.sh"
echo "Health check:        /root/health-check.sh"
echo "Update code:         cd /root/pocket-agent && git pull && systemctl restart pocketagent"
echo ""
echo "Your autonomous AI agent is ready! 🚀"
