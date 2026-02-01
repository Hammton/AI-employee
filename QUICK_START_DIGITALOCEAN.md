# ⚡ Quick Start: Deploy to DigitalOcean in 30 Minutes

## Prerequisites Checklist
- [ ] DigitalOcean account created
- [ ] Payment method added
- [ ] OpenRouter API key ($10 credit added)
- [ ] Composio API key
- [ ] Mem0 API key

---

## 5-Step Deployment

### 1️⃣ Create Droplet (2 minutes)
**Dashboard:** https://cloud.digitalocean.com/

- Click **"Create"** → **"Droplets"**
- **Region:** Choose closest to you
- **Image:** Ubuntu 22.04 LTS
- **Size:** $6/month (1GB RAM)
- **Authentication:** Password
- **Hostname:** `ai-employee-prod`
- Click **"Create Droplet"**
- **Copy the IP address**

### 2️⃣ Connect via SSH (1 minute)
```bash
ssh root@YOUR_DROPLET_IP
```
Enter your password when prompted.

### 3️⃣ Run Deployment Script (10 minutes)
```bash
curl -fsSL https://raw.githubusercontent.com/Hammton/AI-employee/main/deploy_vps.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

**When prompted, enter:**
- Repository: `https://github.com/Hammton/AI-employee.git`
- OpenRouter key: `sk-or-v1-...`
- Composio key: `ak_...`
- Mem0 key: `m0-...`
- Phone: `+1234567890`

### 4️⃣ Connect WhatsApp (5 minutes)
```bash
systemctl stop wpp-bridge
cd /root/pocket-agent/wpp-bridge
DISPLAY=:99 node index.js
```

1. Scan QR code with WhatsApp
2. Wait for "Client is ready!"
3. Press **Ctrl+C**
4. Start service:
```bash
systemctl start wpp-bridge
```

### 5️⃣ Test It! (1 minute)
Send WhatsApp message:
```
Hello! Are you working?
```

---

## Essential Commands

### Check Status
```bash
systemctl status pocketagent
systemctl status wpp-bridge
```

### View Logs
```bash
journalctl -u pocketagent -f
```

### Restart Services
```bash
systemctl restart pocketagent wpp-bridge
```

### Update Code
```bash
cd /root/pocket-agent
git pull
systemctl restart pocketagent
```

---

## Troubleshooting

### Bot not responding?
```bash
journalctl -u pocketagent -f
systemctl restart pocketagent
```

### WhatsApp disconnected?
```bash
systemctl stop wpp-bridge
cd /root/pocket-agent/wpp-bridge
rm -rf tokens/*
DISPLAY=:99 node index.js
# Scan QR, then Ctrl+C
systemctl start wpp-bridge
```

---

## What's Next?

### Connect Tools
```
/connect gmail
/connect googlecalendar
/connect notion
```

### Try Features
```
Remember that I like pizza
Generate an image of a sunset
/help
```

---

## Cost
- **Droplet:** $6/month
- **AI Usage:** $10-30/month
- **Total:** $16-36/month

---

## Support
- **Full Guide:** `DIGITALOCEAN_BEGINNER_GUIDE.md`
- **Logs:** `journalctl -u pocketagent -f`
- **GitHub:** https://github.com/Hammton/AI-employee

🎉 **Your AI employee is live in 30 minutes!**
