# 🚀 Deploy to All Platforms - Step-by-Step Guide

Your code is now on GitHub: https://github.com/Hammton/AI-employee

Let's deploy to all 4 platforms!

---

## 📋 Pre-Deployment Checklist

Before deploying anywhere, make sure you have:

- [x] Code pushed to GitHub ✅
- [ ] OpenRouter API key (https://openrouter.ai/)
- [ ] Composio API key (https://app.composio.dev/)
- [ ] Mem0 API key (https://app.mem0.ai/)
- [ ] Phone number for WhatsApp

---

## 1️⃣ Railway Deployment (Easiest - 5 minutes)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

### Step 2: Login to Railway
```bash
railway login
```
This will open your browser. Sign up/login with GitHub.

### Step 3: Create New Project
```bash
# Navigate to your project folder
cd C:\Users\Administrator\user\Linkedin\pocket-agent

# Initialize Railway project
railway init
```

When prompted:
- Select: "Empty Project"
- Name it: "ai-employee"

### Step 4: Link to GitHub
```bash
# Link your GitHub repo
railway link
```

Or do it via Railway dashboard:
1. Go to https://railway.app/dashboard
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose "Hammton/AI-employee"

### Step 5: Set Environment Variables
```bash
railway variables set OPENROUTER_API_KEY=your_key_here
railway variables set COMPOSIO_API_KEY=your_key_here
railway variables set MEM0_API_KEY=your_key_here
railway variables set USER_PHONE=+1234567890
railway variables set WPP_HEADLESS=true
railway variables set AUTONOMOUS_EXECUTION_APPROVAL=true
```

Or via dashboard:
1. Go to your project
2. Click "Variables"
3. Add each variable

### Step 6: Deploy
```bash
railway up
```

Or it will auto-deploy from GitHub!

### Step 7: Get Your URL
```bash
railway domain
```

Or in dashboard:
1. Click "Settings"
2. Click "Generate Domain"
3. Copy your URL: `https://your-app.up.railway.app`

### Step 8: Connect WhatsApp

**Important:** Railway has ephemeral storage, so WhatsApp connection may disconnect. For production, use VPS or DigitalOcean.

### Railway Status: ✅ DEPLOYED

**Cost:** $5-20/month
**Pros:** Easy, fast deployment
**Cons:** Limited autonomous execution, ephemeral storage

---

## 2️⃣ Render Deployment (Good for Testing - 10 minutes)

### Step 1: Sign Up
1. Go to https://render.com/
2. Sign up with GitHub
3. Authorize Render to access your repos

### Step 2: Create New Web Service
1. Click "New +"
2. Select "Web Service"
3. Connect your GitHub account
4. Select "Hammton/AI-employee"

### Step 3: Configure Service
Fill in these settings:

**Basic Settings:**
- Name: `ai-employee`
- Region: `Oregon (US West)` (or closest to you)
- Branch: `main`
- Root Directory: (leave empty)

**Build Settings:**
- Build Command:
  ```bash
  pip install -r requirements.txt && cd wpp-bridge && npm install && cd ..
  ```
- Start Command:
  ```bash
  bash start_render.sh
  ```

**Instance Type:**
- Select: `Starter` ($7/month) or `Free` (for testing)

### Step 4: Add Environment Variables

Click "Advanced" → "Add Environment Variable"

Add these:
```
OPENROUTER_API_KEY=your_key_here
COMPOSIO_API_KEY=your_key_here
MEM0_API_KEY=your_key_here
USER_PHONE=+1234567890
PORT=8000
WPP_BRIDGE_URL=http://localhost:3001
WPP_HEADLESS=true
AUTONOMOUS_EXECUTION_APPROVAL=true
LLM_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
IMAGE_MODEL=google/gemini-2.5-flash-image
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait 5-10 minutes for build
3. Check logs for any errors

### Step 6: Get Your URL
Your URL will be: `https://ai-employee.onrender.com`

### Step 7: Test
```bash
curl https://ai-employee.onrender.com/health
```

### Render Status: ✅ DEPLOYED

**Cost:** Free tier or $7/month
**Pros:** Free tier available, easy setup
**Cons:** Slower than Railway, limited resources on free tier

---

## 3️⃣ DigitalOcean Deployment (Best for Production - 30 minutes)

### Step 1: Create Account
1. Go to https://www.digitalocean.com/
2. Sign up (get $200 credit with referral)
3. Add payment method

### Step 2: Create Droplet
1. Click "Create" → "Droplets"
2. Choose:
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic
   - **CPU:** Regular ($6/month - 1GB RAM)
   - **Datacenter:** Choose closest to you
   - **Authentication:** SSH Key (recommended) or Password
   - **Hostname:** ai-employee

3. Click "Create Droplet"
4. Wait 1 minute for creation

### Step 3: Get Droplet IP
Copy your droplet's IP address (e.g., `164.92.123.45`)

### Step 4: SSH into Droplet
```bash
ssh root@164.92.123.45
```

If using password, enter it when prompted.

### Step 5: Run Automated Setup
```bash
# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/Hammton/AI-employee/main/deploy_vps.sh -o deploy.sh
chmod +x deploy.sh
./deploy.sh
```

The script will ask for:
1. GitHub repo URL: `https://github.com/Hammton/AI-employee.git`
2. OPENROUTER_API_KEY: (paste your key)
3. COMPOSIO_API_KEY: (paste your key)
4. MEM0_API_KEY: (paste your key)
5. USER_PHONE: (your phone number)

Wait 5-10 minutes for installation.

### Step 6: Connect WhatsApp

After installation completes:

```bash
# Stop WPP Bridge service
systemctl stop wpp-bridge

# Run manually to get QR code
cd /root/pocket-agent/wpp-bridge
DISPLAY=:99 node index.js
```

You'll see a QR code in the terminal. Scan it with WhatsApp:
1. Open WhatsApp on your phone
2. Go to Settings → Linked Devices
3. Tap "Link a Device"
4. Scan the QR code

Once connected, press `Ctrl+C` and start the service:
```bash
systemctl start wpp-bridge
```

### Step 7: Verify Services
```bash
# Check status
systemctl status pocketagent
systemctl status wpp-bridge

# View logs
journalctl -u pocketagent -f
```

### Step 8: Test
```bash
curl http://localhost:8000/health
```

Send a WhatsApp message to test!

### DigitalOcean Status: ✅ DEPLOYED

**Cost:** $6/month
**Pros:** Full control, persistent storage, best for autonomous execution
**Cons:** Requires more setup

---

## 4️⃣ Cloudflare Workers (Advanced - Coming Soon)

**Note:** Cloudflare Workers requires significant refactoring for:
- Durable Objects for state
- KV for caching
- Workers runtime compatibility

**Estimated time:** 2-3 days of development

**For now, use VPS (DigitalOcean) for production.**

---

## 📊 Platform Comparison

| Platform | Cost | Setup Time | Autonomous Execution | Best For |
|----------|------|------------|---------------------|----------|
| **Railway** | $5-20/mo | 5 min | ⚠️ Limited | Quick testing |
| **Render** | $0-7/mo | 10 min | ⚠️ Limited | Free tier testing |
| **DigitalOcean** | $6/mo | 30 min | ✅ Full | **Production** ⭐ |
| **Cloudflare** | $5/mo | 2-3 days | ⚠️ Needs refactor | Future |

**Recommendation:** Use **DigitalOcean** for production!

---

## 🎯 Quick Commands for Each Platform

### Railway
```bash
# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open

# Add variable
railway variables set KEY=value
```

### Render
```bash
# All done via dashboard
# https://dashboard.render.com/
```

### DigitalOcean
```bash
# SSH
ssh root@your-droplet-ip

# View logs
journalctl -u pocketagent -f

# Restart
systemctl restart pocketagent wpp-bridge

# Update code
cd /root/pocket-agent && git pull && systemctl restart pocketagent
```

---

## 🧪 Testing Your Deployment

After deploying to any platform, test with these WhatsApp messages:

### 1. Basic Test
```
"Hello! Are you working?"
```

### 2. Memory Test
```
"Remember that I like pizza"
"What do I like?"
```

### 3. Autonomous Execution Test (DigitalOcean only)
```
"Create a folder called test_deployment"
"List files in current directory"
```

### 4. Web Browsing Test
```
"What's on example.com?"
```

### 5. Tool Test
```
"/tools"
"/help"
```

---

## 🔧 Troubleshooting

### Railway Issues

**Problem:** App crashes on startup
**Solution:**
```bash
railway logs
# Check for missing environment variables
railway variables
```

**Problem:** WhatsApp disconnects
**Solution:** Railway has ephemeral storage. Use DigitalOcean for persistent WhatsApp connection.

### Render Issues

**Problem:** Build fails
**Solution:**
1. Check build logs in dashboard
2. Verify `render.yaml` is correct
3. Check environment variables

**Problem:** Out of memory
**Solution:** Upgrade to paid plan ($7/month)

### DigitalOcean Issues

**Problem:** Can't SSH
**Solution:**
```bash
# Check firewall
ufw status
ufw allow 22
```

**Problem:** Services won't start
**Solution:**
```bash
# Check logs
journalctl -u pocketagent -xe
journalctl -u wpp-bridge -xe

# Restart services
systemctl restart pocketagent wpp-bridge
```

**Problem:** WhatsApp QR code not showing
**Solution:**
```bash
# Make sure Xvfb is running
systemctl status xvfb
systemctl start xvfb

# Try again
cd /root/pocket-agent/wpp-bridge
DISPLAY=:99 node index.js
```

---

## 📈 Monitoring Your Deployments

### Railway
- Dashboard: https://railway.app/dashboard
- Logs: `railway logs`
- Metrics: Available in dashboard

### Render
- Dashboard: https://dashboard.render.com/
- Logs: Click on service → "Logs" tab
- Metrics: Available in dashboard

### DigitalOcean
```bash
# Install monitoring
bash <(curl -Ss https://my-netdata.io/kickstart.sh)

# Access at: http://your-ip:19999
```

---

## 💰 Total Costs

### Option 1: Railway + APIs
- Railway: $5-20/month
- OpenRouter: $10-30/month
- **Total: $15-50/month**

### Option 2: Render + APIs
- Render: $0-7/month
- OpenRouter: $10-30/month
- **Total: $10-37/month**

### Option 3: DigitalOcean + APIs (Recommended)
- DigitalOcean: $6/month
- OpenRouter: $10-30/month
- **Total: $16-36/month**

---

## 🎉 Deployment Complete!

You now have your AI agent deployed on multiple platforms!

### Next Steps:

1. **Choose your primary platform** (DigitalOcean recommended)
2. **Connect WhatsApp** (scan QR code)
3. **Test all features** (send messages)
4. **Monitor performance** (check logs)
5. **Connect more tools** (Gmail, Asana, etc.)

### Useful Links:

- **GitHub Repo:** https://github.com/Hammton/AI-employee
- **Railway Dashboard:** https://railway.app/dashboard
- **Render Dashboard:** https://dashboard.render.com/
- **DigitalOcean Dashboard:** https://cloud.digitalocean.com/

---

## 📞 Quick Reference

### Update Code (All Platforms)

**Railway/Render:** Push to GitHub, auto-deploys

**DigitalOcean:**
```bash
ssh root@your-ip
cd /root/pocket-agent
git pull
systemctl restart pocketagent
```

### View Logs

**Railway:** `railway logs`
**Render:** Dashboard → Logs tab
**DigitalOcean:** `journalctl -u pocketagent -f`

### Restart Services

**Railway:** `railway restart`
**Render:** Dashboard → Manual Deploy
**DigitalOcean:** `systemctl restart pocketagent wpp-bridge`

---

**Your autonomous AI employee is now deployed and ready to work!** 🚀🤖

Need help? Check the logs or refer to DEPLOYMENT_GUIDE.md for detailed troubleshooting.
