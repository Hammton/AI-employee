# 🚀 Deployment Guide - Autonomous PocketAgent

## 🎯 Deployment Strategy

Your agent has **autonomous execution** capabilities, which changes the deployment approach. Here are your options:

## Option 1: VPS Deployment (Recommended for Autonomous Execution) ⭐

**Why VPS?** Autonomous execution needs a persistent environment with shell access.

### Best VPS Providers

| Provider | Cost | Specs | Best For |
|----------|------|-------|----------|
| **DigitalOcean** | $6/mo | 1GB RAM, 1 CPU | Simple setup |
| **Linode** | $5/mo | 1GB RAM, 1 CPU | Budget-friendly |
| **Vultr** | $6/mo | 1GB RAM, 1 CPU | Global locations |
| **Hetzner** | €4/mo | 2GB RAM, 1 CPU | Best value |

### Step-by-Step VPS Deployment

#### 1. Create VPS Instance

**DigitalOcean Example:**
```bash
# Create a droplet
# - Ubuntu 22.04 LTS
# - Basic plan ($6/month)
# - Choose region closest to you
# - Add SSH key
```

#### 2. Connect to VPS
```bash
ssh root@your-server-ip
```

#### 3. Install Dependencies
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Chrome (for WhatsApp)
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# Install Git
apt install -y git
```

#### 4. Clone and Setup Project
```bash
# Clone your repository
git clone https://github.com/your-username/pocket-agent.git
cd pocket-agent

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies for WPP Bridge
cd wpp-bridge
npm install
cd ..
```

#### 5. Configure Environment
```bash
# Create .env file
nano .env
```

Add your configuration:
```env
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_key
COMPOSIO_API_KEY=your_composio_key
MEM0_API_KEY=your_mem0_key

# Server Configuration
PORT=8000
WPP_BRIDGE_URL=http://localhost:3001
WPP_BRIDGE_PORT=3001

# AI Models
LLM_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
IMAGE_MODEL=google/gemini-2.5-flash-image

# WhatsApp
USER_PHONE=+1234567890
WPP_SESSION_NAME=pocket-agent
WPP_HEADLESS=true

# Autonomous Execution (IMPORTANT!)
AUTONOMOUS_EXECUTION_APPROVAL=true
```

#### 6. Setup Systemd Services

**Create Python service:**
```bash
nano /etc/systemd/system/pocketagent.service
```

```ini
[Unit]
Description=PocketAgent AI Assistant
After=network.target

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
```

**Create WPP Bridge service:**
```bash
nano /etc/systemd/system/wpp-bridge.service
```

```ini
[Unit]
Description=WPP Bridge for WhatsApp
After=network.target

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
```

**Create Xvfb service (for headless Chrome):**
```bash
nano /etc/systemd/system/xvfb.service
```

```ini
[Unit]
Description=X Virtual Frame Buffer Service
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :99 -screen 0 1024x768x24
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 7. Start Services
```bash
# Reload systemd
systemctl daemon-reload

# Enable services to start on boot
systemctl enable xvfb
systemctl enable wpp-bridge
systemctl enable pocketagent

# Start services
systemctl start xvfb
systemctl start wpp-bridge
systemctl start pocketagent

# Check status
systemctl status pocketagent
systemctl status wpp-bridge
```

#### 8. Connect WhatsApp

**First time only:**
```bash
# Temporarily run WPP Bridge in foreground to scan QR
cd /root/pocket-agent/wpp-bridge
DISPLAY=:99 node index.js

# Scan QR code with your phone
# Once connected, press Ctrl+C
# Then start the service: systemctl start wpp-bridge
```

#### 9. Setup Firewall
```bash
# Allow SSH
ufw allow 22

# Allow HTTP/HTTPS (if you want web access)
ufw allow 80
ufw allow 443

# Enable firewall
ufw enable
```

#### 10. Monitor Logs
```bash
# View PocketAgent logs
journalctl -u pocketagent -f

# View WPP Bridge logs
journalctl -u wpp-bridge -f

# View all logs
journalctl -f
```

### VPS Deployment Complete! ✅

Your agent is now running 24/7 with:
- ✅ Autonomous execution enabled
- ✅ WhatsApp connected
- ✅ All features working
- ✅ Auto-restart on failure

---

## Option 2: Railway (Limited Autonomous Execution)

**Note:** Railway works but has limitations for autonomous execution (no persistent shell access).

### Railway Deployment

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
railway init

# Set environment variables
railway variables set OPENROUTER_API_KEY=your_key
railway variables set COMPOSIO_API_KEY=your_key
railway variables set MEM0_API_KEY=your_key
railway variables set WPP_HEADLESS=true
railway variables set AUTONOMOUS_EXECUTION_APPROVAL=true

# Deploy
railway up
```

**Limitations:**
- ⚠️ Ephemeral file system (files don't persist)
- ⚠️ Limited shell access
- ⚠️ WhatsApp session may disconnect
- ✅ Good for testing
- ✅ Easy deployment

**Cost:** $5-20/month

---

## Option 3: Docker Deployment (Advanced)

For those who want containerization:

### Create Dockerfile

```dockerfile
FROM ubuntu:22.04

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    nodejs \
    npm \
    wget \
    gnupg \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Install Node dependencies
RUN cd wpp-bridge && npm install

# Expose ports
EXPOSE 8000 3001

# Start script
CMD ["bash", "-c", "Xvfb :99 -screen 0 1024x768x24 & cd wpp-bridge && node index.js & python3 main_v2.py"]
```

### Deploy with Docker

```bash
# Build image
docker build -t pocketagent .

# Run container
docker run -d \
  --name pocketagent \
  -p 8000:8000 \
  -p 3001:3001 \
  -e OPENROUTER_API_KEY=your_key \
  -e COMPOSIO_API_KEY=your_key \
  -e MEM0_API_KEY=your_key \
  -v $(pwd)/wpp-bridge/tokens:/app/wpp-bridge/tokens \
  pocketagent
```

---

## Option 4: Home Server / Raspberry Pi

Perfect for local deployment with full control:

### Requirements
- Raspberry Pi 4 (4GB+ RAM) or any Linux machine
- Ubuntu Server 22.04
- Stable internet connection

### Setup
Follow the same steps as VPS deployment, but:
1. Use your local machine
2. No need for cloud provider
3. Free hosting!
4. Full control

**Pros:**
- ✅ Free hosting
- ✅ Full control
- ✅ No bandwidth limits
- ✅ Complete privacy

**Cons:**
- ⚠️ Need to manage hardware
- ⚠️ Need stable internet
- ⚠️ Need to handle power outages

---

## 🔐 Security Best Practices

### 1. Firewall Configuration
```bash
# Only allow necessary ports
ufw allow 22    # SSH
ufw allow 80    # HTTP (optional)
ufw allow 443   # HTTPS (optional)
ufw enable
```

### 2. SSH Key Authentication
```bash
# Disable password authentication
nano /etc/ssh/sshd_config

# Set: PasswordAuthentication no
# Restart SSH: systemctl restart sshd
```

### 3. Fail2Ban (Prevent brute force)
```bash
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

### 4. Regular Updates
```bash
# Create update script
nano /root/update.sh
```

```bash
#!/bin/bash
apt update
apt upgrade -y
cd /root/pocket-agent
git pull
source venv/bin/activate
pip install -r requirements.txt
systemctl restart pocketagent
```

```bash
chmod +x /root/update.sh

# Run weekly via cron
crontab -e
# Add: 0 2 * * 0 /root/update.sh
```

### 5. Backup Strategy
```bash
# Backup script
nano /root/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /root/backups/pocket-agent-$DATE.tar.gz \
  /root/pocket-agent/.env \
  /root/pocket-agent/wpp-bridge/tokens \
  /root/pocket-agent/memory

# Keep only last 7 backups
find /root/backups -name "pocket-agent-*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /root/backup.sh

# Run daily via cron
crontab -e
# Add: 0 3 * * * /root/backup.sh
```

---

## 📊 Monitoring & Maintenance

### 1. Health Check Script
```bash
nano /root/health-check.sh
```

```bash
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
```

```bash
chmod +x /root/health-check.sh

# Run every 5 minutes
crontab -e
# Add: */5 * * * * /root/health-check.sh
```

### 2. Log Rotation
```bash
nano /etc/logrotate.d/pocketagent
```

```
/var/log/pocketagent/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### 3. Monitoring Dashboard (Optional)

Install Netdata for real-time monitoring:
```bash
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access at: http://your-server-ip:19999
```

---

## 🧪 Testing Deployment

### 1. Test Health Endpoint
```bash
curl http://your-server-ip:8000/health
# Should return: {"status": "healthy"}
```

### 2. Test WhatsApp Status
```bash
curl http://your-server-ip:8000/whatsapp/status
# Should return: {"connected": true}
```

### 3. Send Test Message
Send a WhatsApp message:
```
"Hello! Are you working?"
```

Expected response:
```
"Yes! I'm running on your VPS with autonomous execution enabled. 
Try asking me to create a folder or list files!"
```

### 4. Test Autonomous Execution
```
"Create a folder called test_deployment"
```

Expected response:
```
"✅ Created folder 'test_deployment' in /root/pocket-agent"
```

---

## 💰 Cost Comparison

| Option | Monthly Cost | Autonomous Execution | Best For |
|--------|-------------|---------------------|----------|
| **VPS (DigitalOcean)** | $6 | ✅ Full | Production |
| **VPS (Hetzner)** | €4 | ✅ Full | Budget |
| **Railway** | $5-20 | ⚠️ Limited | Testing |
| **Home Server** | $0 | ✅ Full | DIY |
| **Raspberry Pi** | $0 | ✅ Full | Learning |

**Recommended:** VPS for production, Home Server for personal use

---

## 🚨 Troubleshooting

### Issue: WhatsApp Disconnects
```bash
# Check WPP Bridge logs
journalctl -u wpp-bridge -n 50

# Restart service
systemctl restart wpp-bridge

# If persistent, delete tokens and reconnect
rm -rf /root/pocket-agent/wpp-bridge/tokens/*
systemctl restart wpp-bridge
```

### Issue: High Memory Usage
```bash
# Check memory
free -h

# Restart services
systemctl restart pocketagent
systemctl restart wpp-bridge
```

### Issue: Autonomous Execution Not Working
```bash
# Check if executor is enabled
grep AUTONOMOUS_EXECUTION /root/pocket-agent/.env

# Check logs
journalctl -u pocketagent | grep "Autonomous Executor"

# Should see: "✅ Autonomous Executor initialized"
```

### Issue: Services Won't Start
```bash
# Check service status
systemctl status pocketagent
systemctl status wpp-bridge

# Check logs
journalctl -xe

# Verify Python environment
source /root/pocket-agent/venv/bin/activate
python -c "from kernel import AgentKernel; print('OK')"
```

---

## 📚 Quick Reference

### Essential Commands

```bash
# Start services
systemctl start pocketagent wpp-bridge

# Stop services
systemctl stop pocketagent wpp-bridge

# Restart services
systemctl restart pocketagent wpp-bridge

# View logs
journalctl -u pocketagent -f
journalctl -u wpp-bridge -f

# Update code
cd /root/pocket-agent
git pull
systemctl restart pocketagent

# Backup
/root/backup.sh

# Health check
/root/health-check.sh
```

---

## 🎉 Deployment Complete!

Your autonomous AI agent is now:
- ✅ Running 24/7 on a VPS
- ✅ Connected to WhatsApp
- ✅ Autonomous execution enabled
- ✅ Intelligent memory active
- ✅ Web browsing working
- ✅ 565+ tools available
- ✅ Auto-restart on failure
- ✅ Monitored and backed up

**Your AI remote worker is LIVE!** 🚀

---

## 📞 Support

- **Documentation:** See [docs/](docs/) folder
- **Issues:** Check logs with `journalctl`
- **Updates:** `git pull && systemctl restart pocketagent`
- **Backup:** Run `/root/backup.sh`

**Next:** Send a message and watch your autonomous agent work! 🤖
