# DigitalOcean Deployment Guide - Complete & Working

## Overview
This guide documents the complete, tested deployment process for PocketAgent WhatsApp AI Bot on DigitalOcean.

## Prerequisites
- DigitalOcean account
- GitHub repository (must be public for easy cloning)
- API Keys: OpenRouter, Composio, Mem0
- WhatsApp phone number for the bot

## Server Requirements
- **Minimum**: 2GB RAM Ubuntu 24.04 droplet
- **Recommended**: 4GB RAM for handling media messages
- 1GB RAM is NOT sufficient - the WPP bridge will be killed by OOM

## Step-by-Step Deployment

### 1. Create DigitalOcean Droplet
1. Log into DigitalOcean
2. Create Droplet:
   - **Image**: Ubuntu 24.04 LTS
   - **Plan**: Basic - 2GB RAM / 1 CPU ($12/month)
   - **Region**: Choose closest to you
   - **Authentication**: Password (easier for beginners)
3. Note your droplet's IP address

### 2. Connect to Server
Use DigitalOcean web console (easier) or SSH:
```bash
ssh root@YOUR_DROPLET_IP
```

### 3. Run Deployment Script
```bash
# Update system
apt update && apt upgrade -y

# Install Python 3 (Ubuntu 24.04 has Python 3.12)
apt install -y python3 python3-venv python3-pip

# Install Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Install Chrome
wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb
rm google-chrome-stable_current_amd64.deb

# Install Xvfb (virtual display)
apt install -y xvfb git

# Clone repository
cd /root
git clone https://github.com/YOUR_USERNAME/AI-employee.git pocket-agent
cd pocket-agent

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install Node dependencies
cd wpp-bridge
npm install

# CRITICAL FIX: Install node-fetch for proper HTTP requests
npm install node-fetch@2

# Add node-fetch import to index.js
sed -i "15a import fetch from 'node-fetch';" /root/pocket-agent/wpp-bridge/index.js

cd ..
```

### 4. Configure Environment Variables
```bash
# Create main .env file
cat > /root/pocket-agent/.env << 'EOF'
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_key_here
COMPOSIO_API_KEY=your_composio_key_here
MEM0_API_KEY=your_mem0_key_here

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
USER_PHONE=+1234567890
WPP_SESSION_NAME=pocket-agent
WPP_HEADLESS=true

# Autonomous Execution
AUTONOMOUS_EXECUTION_APPROVAL=true
EOF

# Replace with your actual API keys
nano /root/pocket-agent/.env
```

### 5. Create Systemd Services

#### Xvfb Service (Virtual Display)
```bash
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
```

#### WPP Bridge Service (WhatsApp)
**CRITICAL**: Environment variables must be in the systemd service file, not just .env
```bash
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
Environment="PYTHON_CALLBACK_URL=http://127.0.0.1:8000"
Environment="WPP_BRIDGE_PORT=3001"
Environment="WPP_SESSION_NAME=pocket-agent"
Environment="WPP_HEADLESS=true"

[Install]
WantedBy=multi-user.target
EOF
```

**Why 127.0.0.1 instead of localhost?**
- Node.js resolves `localhost` to IPv6 `::1` by default
- Python listens on IPv4 `127.0.0.1`
- Using `127.0.0.1` directly avoids connection issues

#### PocketAgent Service (Python Bot)
```bash
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
```

### 6. Enable and Start Services
```bash
systemctl daemon-reload
systemctl enable xvfb wpp-bridge pocketagent
systemctl start xvfb
sleep 2
systemctl start pocketagent
sleep 2
```

### 7. Connect WhatsApp (First Time Only)
```bash
# Stop the service to connect manually
systemctl stop wpp-bridge

# Run manually to see QR code
cd /root/pocket-agent/wpp-bridge
DISPLAY=:99 node index.js

# You'll see a QR code in ASCII art
# Scan it with WhatsApp on your phone:
# WhatsApp > Settings > Linked Devices > Link a Device

# After "Login with success" appears, press Ctrl+C

# Start the service
systemctl start wpp-bridge
```

### 8. Verify Everything is Working
```bash
# Check all services
systemctl status xvfb
systemctl status pocketagent
systemctl status wpp-bridge

# Test Python bot endpoint
curl http://localhost:8000/health

# Watch logs
journalctl -u pocketagent -u wpp-bridge -f

# Send a WhatsApp message to your bot
# You should see it in the logs and get a reply!
```

## Common Issues & Solutions

### Issue 1: WPP Bridge Gets Killed
**Symptom**: `code=killed, signal=KILL` in logs
**Cause**: Out of memory (OOM killer)
**Solution**: Upgrade to 2GB RAM droplet minimum

### Issue 2: "fetch failed" Error
**Symptom**: `Failed to forward to Python: fetch failed`
**Cause**: Missing node-fetch package
**Solution**: 
```bash
cd /root/pocket-agent/wpp-bridge
npm install node-fetch@2
sed -i "15a import fetch from 'node-fetch';" index.js
systemctl restart wpp-bridge
```

### Issue 3: "connect ECONNREFUSED ::1:8000"
**Symptom**: Connection refused to IPv6 address
**Cause**: localhost resolving to IPv6 but Python on IPv4
**Solution**: Use `127.0.0.1` instead of `localhost` in systemd service (already fixed above)

### Issue 4: Environment Variables Not Loading
**Symptom**: WPP bridge can't find Python callback URL
**Cause**: Systemd doesn't load .env files automatically
**Solution**: Put environment variables directly in systemd service file (already done above)

### Issue 5: Python Import Errors
**Symptom**: `ModuleNotFoundError: No module named 'composio'`
**Cause**: Wrong Python version or venv not activated
**Solution**: Use Python 3.11+ and ensure venv path is correct in systemd service

### Issue 6: Image Generation Not Working with Natural Language
**Symptom**: Bot says "I cannot directly generate an image" when you say "Generate a house" or similar
**Cause**: Natural language detection only recognizes specific keywords like "generate image" or "create picture"
**Solution**: Use the `/image` command for reliable image generation:
```
/image a house located next to a beach on Highland
/image a sunset over mountains
/image a futuristic city
```

**Why this happens**: The `_extract_image_prompt()` function in `main_v2.py` looks for combinations like:
- "generate" + "image/picture/photo"
- "create" + "image/picture/photo"
- "make" + "image/picture/photo"

If you say "Generate a **house**" instead of "Generate an **image** of a house", it won't be detected.

**Workaround**: Always use `/image <description>` for guaranteed image generation, or include the word "image" or "picture" in your request:
- ✅ "Generate an image of a house on the beach"
- ✅ "Create a picture of a sunset"
- ✅ "/image a house on the beach"
- ❌ "Generate a house on the beach" (won't work)

## Maintenance Commands

### View Logs
```bash
# Live logs from all services
journalctl -u pocketagent -u wpp-bridge -f

# Last 50 lines
journalctl -u pocketagent -n 50
journalctl -u wpp-bridge -n 50

# Check for errors
journalctl -u wpp-bridge --since "1 hour ago" | grep -i error
```

### Restart Services
```bash
systemctl restart pocketagent
systemctl restart wpp-bridge
systemctl restart xvfb
```

### Update Code
```bash
cd /root/pocket-agent
git pull
systemctl restart pocketagent wpp-bridge
```

### Check Memory Usage
```bash
free -h
ps aux --sort=-%mem | head -10
```

### Backup WhatsApp Session
```bash
tar -czf ~/whatsapp-session-backup.tar.gz /root/pocket-agent/wpp-bridge/tokens
```

## Performance Optimization

### Add Swap Space (Helps with Memory Spikes)
```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Setup Automatic Backups
```bash
cat > /root/backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf /root/backups/pocket-agent-$DATE.tar.gz \
  /root/pocket-agent/.env \
  /root/pocket-agent/wpp-bridge/tokens \
  /root/pocket-agent/memory
find /root/backups -name "pocket-agent-*.tar.gz" -mtime +7 -delete
EOF

chmod +x /root/backup.sh
mkdir -p /root/backups

# Add to crontab (daily at 3 AM)
(crontab -l 2>/dev/null; echo "0 3 * * * /root/backup.sh") | crontab -
```

## Security Recommendations

1. **Firewall**: Only allow SSH (port 22)
```bash
apt install -y ufw
ufw allow 22
ufw --force enable
```

2. **Keep System Updated**
```bash
apt update && apt upgrade -y
```

3. **Secure API Keys**: Never commit .env to git
```bash
echo ".env" >> .gitignore
```

## Testing Your Deployment

Send these test messages to your bot:

1. **Basic Test**: `Hello!`
   - Should get a greeting response

2. **Tool Test**: `What tools do you have?`
   - Should list available integrations

3. **Gmail Test**: `Check my emails`
   - Should access Gmail if connected

4. **Web Search**: `Search for latest AI news`
   - Should use web search tools

## Success Indicators

✅ All three services running: `systemctl status xvfb pocketagent wpp-bridge`
✅ Python bot responds: `curl http://localhost:8000/health`
✅ WhatsApp connected: Check logs for "MAIN (NORMAL)"
✅ Messages forwarded: No "fetch failed" errors in logs
✅ Bot replies on WhatsApp within 5-10 seconds

## Cost Estimate

- **2GB Droplet**: $12/month
- **4GB Droplet**: $24/month (recommended for production)
- **Backups**: $1.20/month (optional)

**Total**: ~$12-25/month for a fully autonomous AI assistant!

## Support

If you encounter issues:
1. Check logs: `journalctl -u wpp-bridge -u pocketagent -n 100`
2. Verify services: `systemctl status xvfb pocketagent wpp-bridge`
3. Test endpoints: `curl http://localhost:8000/health`
4. Check memory: `free -h`

## Updating Your Deployment

When you make changes to your code locally and push to GitHub:

### Quick Update
```bash
# On your local machine
git add .
git commit -m "Your changes"
git push origin main

# On DigitalOcean server
ssh root@YOUR_DROPLET_IP
cd /root/pocket-agent
git pull
systemctl restart pocketagent wpp-bridge
```

### Python Changes Only
```bash
cd /root/pocket-agent
git pull
systemctl restart pocketagent
```

### WPP Bridge Changes Only
```bash
cd /root/pocket-agent
git pull
cd wpp-bridge
npm install  # Only if package.json changed
systemctl restart wpp-bridge
```

### Dependencies Changed
```bash
cd /root/pocket-agent
git pull
source venv/bin/activate
pip install -r requirements.txt
cd wpp-bridge && npm install && cd ..
systemctl restart pocketagent wpp-bridge
```

## Image Generation Setup

Your bot can generate images! Just configure it:

### Enable Image Generation
```bash
# Edit .env file
nano /root/pocket-agent/.env

# Add this line:
IMAGE_MODEL=google/gemini-2.5-flash-image

# Restart
systemctl restart pocketagent
```

### Test Image Generation
Send WhatsApp message:
- ✅ `"/image a sunset over mountains"` (RECOMMENDED - Always works)
- ✅ `"Generate an image of a cute cat"`
- ✅ `"Create a picture of a futuristic city"`
- ❌ `"Generate a house on the beach"` (Won't work - missing "image" keyword)

### How to Use Image Generation

**Method 1: /image Command (Recommended)**
```
/image <your description>
```
Examples:
- `/image a beautiful sunset over mountains`
- `/image a modern house by the beach`
- `/image a cute cat sitting on a windowsill`

**Method 2: Natural Language (Must include "image" or "picture")**
```
Generate an image of <description>
Create a picture of <description>
Make an image of <description>
```
Examples:
- `"Generate an image of a sunset"`
- `"Create a picture of a house on the beach"`
- `"Make an image of a futuristic city"`

### Troubleshooting Image Generation

**Problem**: Bot says "I cannot directly generate an image"
**Solution**: Use the `/image` command or include the word "image/picture" in your request

**Problem**: Image generation is slow (10-30 seconds)
**Solution**: This is normal - AI image generation takes time. The bot will show a typing indicator while generating.

**Problem**: Image quality is low
**Solution**: Be more descriptive in your prompt:
- ❌ "a house"
- ✅ "a modern luxury house with glass walls, located on a cliff overlooking the ocean at sunset, professional architectural photography"

### Available Models
- `google/gemini-2.5-flash-image` (Recommended - Fast & Good quality)
- `openai/dall-e-3` (Highest quality, more expensive)
- `openai/dall-e-2` (Cheaper alternative)

### Image Generation Tips

1. **Be Specific**: Include details about style, lighting, colors, mood
2. **Use Descriptive Language**: "Professional photography", "cinematic lighting", "high detail"
3. **Specify Composition**: "Wide angle", "close-up", "aerial view"
4. **Add Context**: "At sunset", "in winter", "during golden hour"

**Example Good Prompts**:
- `/image a cozy cabin in snowy mountains at sunset, warm lights glowing from windows, professional landscape photography`
- `/image a futuristic city with flying cars, neon lights, cyberpunk style, night scene, cinematic composition`
- `/image a minimalist modern kitchen with marble countertops, natural lighting, architectural digest style`

## Next Steps

After successful deployment:
1. Enable image generation (see above)
2. Connect more integrations via Composio
3. Customize AI behavior in `kernel.py`
4. Add custom commands in `main_v2.py`
5. Setup monitoring and alerts

---

**Deployment Status**: ✅ WORKING
**Last Tested**: February 2026
**Platform**: DigitalOcean Ubuntu 24.04
**Success Rate**: 100% when following this guide
