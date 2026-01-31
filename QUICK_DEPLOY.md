# ⚡ Quick Deploy Guide - Get Running in 10 Minutes

## 🎯 Fastest Way to Deploy

### Option 1: One-Command VPS Deploy (Recommended)

**Requirements:**
- Fresh Ubuntu 22.04 VPS
- Root access
- 5-10 minutes

**Steps:**

1. **SSH into your VPS**
```bash
ssh root@your-server-ip
```

2. **Run deployment script**
```bash
curl -fsSL https://raw.githubusercontent.com/your-username/pocket-agent/main/deploy_vps.sh | bash
```

3. **Connect WhatsApp**
```bash
systemctl stop wpp-bridge
cd /root/pocket-agent/wpp-bridge
DISPLAY=:99 node index.js
# Scan QR code with your phone
# Press Ctrl+C after connected
systemctl start wpp-bridge
```

4. **Test it!**
Send a WhatsApp message:
```
"Hello! Create a folder called test"
```

**Done!** ✅

---

### Option 2: Manual VPS Deploy

If you prefer manual control:

```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Install dependencies
apt install -y python3.11 python3.11-venv python3-pip nodejs npm git wget xvfb

# 3. Install Chrome
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb

# 4. Clone repo
cd /root
git clone https://github.com/your-username/pocket-agent.git
cd pocket-agent

# 5. Setup Python
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 6. Setup Node
cd wpp-bridge && npm install && cd ..

# 7. Configure .env
nano .env
# Add your API keys

# 8. Create services (see DEPLOYMENT_GUIDE.md)

# 9. Start services
systemctl start xvfb wpp-bridge pocketagent
```

---

### Option 3: Railway (Quick Test)

**For testing only** (limited autonomous execution):

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy
railway init
railway variables set OPENROUTER_API_KEY=your_key
railway variables set COMPOSIO_API_KEY=your_key
railway variables set MEM0_API_KEY=your_key
railway up
```

**Note:** Railway has limitations for autonomous execution.

---

## 🔑 Required API Keys

Get these before deploying:

1. **OpenRouter** - https://openrouter.ai/
   - Sign up
   - Get API key
   - Add $10 credit

2. **Composio** - https://app.composio.dev/
   - Sign up
   - Get API key
   - Free tier available

3. **Mem0** - https://app.mem0.ai/
   - Sign up
   - Get API key
   - Free tier (1000 memories)

---

## 📊 Cost Breakdown

### VPS Option (Recommended)
- **VPS:** $5-6/month (DigitalOcean, Linode, Hetzner)
- **OpenRouter:** $10-30/month (AI models)
- **Composio:** $0 (free tier)
- **Mem0:** $0 (free tier)
- **Total:** $15-36/month

### Railway Option
- **Railway:** $5-20/month
- **OpenRouter:** $10-30/month
- **Composio:** $0
- **Mem0:** $0
- **Total:** $15-50/month

---

## ✅ Post-Deployment Checklist

After deployment:

- [ ] Services running: `systemctl status pocketagent wpp-bridge`
- [ ] WhatsApp connected: `curl http://localhost:8000/whatsapp/status`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] Test message sent
- [ ] Agent responded
- [ ] Autonomous execution tested

---

## 🧪 Quick Tests

### 1. Health Check
```bash
curl http://your-server-ip:8000/health
```
Expected: `{"status": "healthy"}`

### 2. WhatsApp Status
```bash
curl http://your-server-ip:8000/whatsapp/status
```
Expected: `{"connected": true}`

### 3. Test Messages

Send these via WhatsApp:

**Memory Test:**
```
"Remember that I like pizza"
"What do I like?"
```

**Autonomous Execution Test:**
```
"Create a folder called my_test"
"List files in current directory"
```

**Web Browsing Test:**
```
"What's on example.com?"
```

**Tool Test:**
```
"/tools"
```

---

## 🚨 Common Issues

### Issue: WhatsApp won't connect
**Solution:**
```bash
# Delete tokens and reconnect
rm -rf /root/pocket-agent/wpp-bridge/tokens/*
systemctl restart wpp-bridge
# Scan QR again
```

### Issue: Services won't start
**Solution:**
```bash
# Check logs
journalctl -u pocketagent -xe
journalctl -u wpp-bridge -xe

# Verify Python
source /root/pocket-agent/venv/bin/activate
python -c "from kernel import AgentKernel; print('OK')"
```

### Issue: Autonomous execution not working
**Solution:**
```bash
# Check .env
grep AUTONOMOUS_EXECUTION /root/pocket-agent/.env

# Should be: AUTONOMOUS_EXECUTION_APPROVAL=true

# Restart
systemctl restart pocketagent
```

---

## 📞 Quick Commands

```bash
# View logs
journalctl -u pocketagent -f

# Restart services
systemctl restart pocketagent wpp-bridge

# Update code
cd /root/pocket-agent && git pull && systemctl restart pocketagent

# Backup
tar -czf backup.tar.gz .env wpp-bridge/tokens memory/

# Check status
systemctl status pocketagent wpp-bridge
```

---

## 🎉 You're Done!

Your autonomous AI agent is now:
- ✅ Running 24/7
- ✅ Connected to WhatsApp
- ✅ Autonomous execution enabled
- ✅ Intelligent memory active
- ✅ Web browsing working
- ✅ 565+ tools available

**Send a message and watch it work!** 🚀

---

## 📚 Next Steps

1. **Connect more tools:**
   - Send: `/connect gmail`
   - Send: `/connect asana`
   - Send: `/connect notion`

2. **Test autonomous features:**
   - "Create a project structure"
   - "Backup my files"
   - "Show me system info"

3. **Explore capabilities:**
   - "What can you do?"
   - "/help"
   - "Generate an image of a sunset"

4. **Monitor and optimize:**
   - Check logs regularly
   - Run health checks
   - Backup important data

---

**Need help?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

**Your AI remote worker is ready!** 🤖💼
