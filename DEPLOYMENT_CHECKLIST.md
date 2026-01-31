# 🚀 PocketAgent Deployment Checklist

## ✅ Pre-Deployment Verification

### Environment Setup
- [x] Python 3.8+ installed
- [x] Node.js 16+ installed
- [x] Chrome browser installed
- [x] All dependencies installed (`pip install -r requirements.txt`)
- [x] WPP Bridge dependencies installed (`cd wpp-bridge && npm install`)

### API Keys Configured
- [x] OPENROUTER_API_KEY set in .env
- [x] COMPOSIO_API_KEY set in .env
- [x] MEM0_API_KEY set in .env
- [x] All keys tested and working

### Core Features Tested
- [x] Kernel initialization working
- [x] Mem0 integration tested (`python test_mem0_integration.py`)
- [x] Tool loading verified
- [x] Web browsing working (Anchor Browser)
- [x] Multi-user support tested

### Code Quality
- [x] No syntax errors
- [x] Error handling in place
- [x] Logging configured
- [x] Security best practices followed
- [x] .gitignore configured
- [x] No sensitive data in code

### Documentation
- [x] README.md updated
- [x] DEPLOYMENT_READY.md created
- [x] MEM0_INTEGRATION_GUIDE.md created
- [x] All features documented
- [x] Troubleshooting guide included

---

## 🎯 Deployment Steps

### Step 1: Choose Platform

Select one deployment option:

#### Option A: Railway (Recommended) ⭐
**Pros:** Easy setup, automatic deployments, good for Node.js + Python
**Cost:** $5-20/month
**Time:** 15 minutes

- [ ] Install Railway CLI: `npm install -g @railway/cli`
- [ ] Login: `railway login`
- [ ] Initialize: `railway init`
- [ ] Set variables (see below)
- [ ] Deploy: `railway up`

#### Option B: Render
**Pros:** Free tier available, good for Python apps
**Cost:** Free tier or $7+/month
**Time:** 20 minutes

- [ ] Push code to GitHub
- [ ] Connect repo in Render dashboard
- [ ] Add environment variables
- [ ] Deploy

#### Option C: VPS (DigitalOcean, Linode, etc.)
**Pros:** Full control, predictable pricing
**Cost:** $5-20/month
**Time:** 30 minutes

- [ ] SSH into server
- [ ] Clone repository
- [ ] Install dependencies
- [ ] Setup systemd service
- [ ] Start services

---

### Step 2: Set Environment Variables

Required variables for all platforms:

```bash
# Required API Keys
OPENROUTER_API_KEY=your_openrouter_key_here
COMPOSIO_API_KEY=your_composio_key_here
MEM0_API_KEY=your_mem0_key_here

# Server Configuration
PORT=8000
WPP_BRIDGE_URL=http://localhost:3001
WPP_BRIDGE_PORT=3001

# AI Models (Optional - defaults provided)
LLM_MODEL=google/gemini-3-flash-preview
VISION_MODEL=google/gemini-3-flash-preview
IMAGE_MODEL=google/gemini-2.5-flash-image
AUDIO_MODEL=google/gemini-3-flash-preview
TTS_MODEL=google/gemini-3-flash-preview

# WhatsApp
USER_PHONE=+1234567890
WPP_SESSION_NAME=pocket-agent
WPP_HEADLESS=true  # Set to true for production
```

**Railway:**
```bash
railway variables set OPENROUTER_API_KEY=your_key
railway variables set COMPOSIO_API_KEY=your_key
railway variables set MEM0_API_KEY=your_key
railway variables set WPP_HEADLESS=true
```

**Render:**
- Add in dashboard under "Environment" tab

**VPS:**
- Create `.env` file in project root
- Copy variables above

---

### Step 3: Deploy Application

#### Railway
```bash
railway up
```
- [ ] Deployment started
- [ ] Build successful
- [ ] Services running
- [ ] URL generated

#### Render
- [ ] Push to GitHub
- [ ] Render auto-deploys
- [ ] Build successful
- [ ] Services running

#### VPS
```bash
# Start Python server
python main_v2.py &

# Start WPP Bridge
cd wpp-bridge
npm start &
```
- [ ] Python server running
- [ ] WPP Bridge running
- [ ] Both services healthy

---

### Step 4: Connect WhatsApp

- [ ] Access WPP Bridge (port 3001)
- [ ] QR code displayed
- [ ] Scan QR with WhatsApp
- [ ] Connection successful
- [ ] Status shows "connected"

**Verify:**
```bash
curl http://your-server:3001/status
# Should return: {"ready": true, "connected": true}
```

---

### Step 5: Test Deployment

#### Basic Tests
- [ ] Health check: `curl http://your-server:8000/health`
- [ ] WhatsApp status: `curl http://your-server:8000/whatsapp/status`
- [ ] Send test message via WhatsApp
- [ ] Receive response from agent

#### Feature Tests
Send these messages via WhatsApp:

1. **Memory Test**
   - [ ] Send: "Remember that I'm a vegetarian"
   - [ ] Send: "What do you know about my diet?"
   - [ ] Verify: Agent remembers

2. **Tool Test**
   - [ ] Send: "/tools"
   - [ ] Verify: Shows connected tools

3. **Web Browsing Test** (if Anchor Browser connected)
   - [ ] Send: "What's on example.com?"
   - [ ] Verify: Agent visits and extracts content

4. **Image Generation Test**
   - [ ] Send: "/image a sunset over mountains"
   - [ ] Verify: Receives generated image

---

### Step 6: Monitor & Verify

#### Check Logs
- [ ] Python server logs show no errors
- [ ] WPP Bridge logs show "connected"
- [ ] Mem0 operations logging correctly
- [ ] Tool executions working

#### Performance Metrics
- [ ] Response time < 5 seconds
- [ ] Memory usage < 512MB
- [ ] No error spikes
- [ ] All features working

#### Mem0 Verification
```bash
# Run test script
python test_mem0_integration.py
```
- [ ] Memory storage working
- [ ] Context retrieval working
- [ ] Semantic search working

---

## 📊 Post-Deployment Tasks

### Immediate (Day 1)
- [ ] Monitor logs for errors
- [ ] Test all major features
- [ ] Verify Mem0 working
- [ ] Check tool connections
- [ ] Document any issues

### Short-term (Week 1)
- [ ] Connect additional tools (Notion, Slack, etc.)
- [ ] Test with multiple users
- [ ] Gather user feedback
- [ ] Fix any bugs
- [ ] Optimize performance

### Medium-term (Month 1)
- [ ] Add multi-channel support (Telegram, Discord)
- [ ] Implement background worker
- [ ] Add analytics dashboard
- [ ] Review and optimize costs
- [ ] Scale infrastructure if needed

---

## 🐛 Troubleshooting

### Issue: Deployment Failed
**Check:**
- [ ] All dependencies in requirements.txt
- [ ] Environment variables set correctly
- [ ] Build logs for errors
- [ ] Platform-specific requirements met

### Issue: WhatsApp Not Connecting
**Check:**
- [ ] WPP Bridge running
- [ ] Chrome installed on server
- [ ] WPP_HEADLESS set correctly
- [ ] Firewall not blocking
- [ ] QR code accessible

### Issue: Mem0 Not Working
**Check:**
- [ ] MEM0_API_KEY set correctly
- [ ] API key has quota remaining
- [ ] Run: `python test_mem0_integration.py`
- [ ] Check Mem0 dashboard

### Issue: Tools Not Loading
**Check:**
- [ ] COMPOSIO_API_KEY set correctly
- [ ] User has connected apps
- [ ] Run: `python scripts/check_user_connections.py`
- [ ] Check Composio dashboard

### Issue: High Memory Usage
**Check:**
- [ ] Monitor with: `ps aux | grep python`
- [ ] Check for memory leaks
- [ ] Restart services if needed
- [ ] Consider upgrading plan

---

## 💰 Cost Monitoring

### Monthly Budget
- [ ] Hosting: $5-20
- [ ] OpenRouter: $10-30
- [ ] Composio: $0 (free tier)
- [ ] Mem0: $0-20 (free tier)
- [ ] Total: $15-70

### Cost Optimization
- [ ] Monitor OpenRouter usage
- [ ] Use cheaper models when possible
- [ ] Cache responses where appropriate
- [ ] Review Mem0 memory count
- [ ] Optimize tool calls

---

## 📈 Success Metrics

### Week 1 Goals
- [ ] 100% uptime
- [ ] < 5s average response time
- [ ] < 1% error rate
- [ ] 5+ active users
- [ ] All features working

### Month 1 Goals
- [ ] 99.9% uptime
- [ ] < 3s average response time
- [ ] < 0.5% error rate
- [ ] 20+ active users
- [ ] Positive user feedback

---

## 🎉 Deployment Complete!

Once all items are checked:

- [ ] All pre-deployment checks passed
- [ ] Platform deployed successfully
- [ ] WhatsApp connected
- [ ] All features tested
- [ ] Monitoring in place
- [ ] Documentation updated

**Your AI agent is now LIVE!** 🚀

---

## 📞 Support Resources

- **Documentation:** [docs/](docs/) folder
- **Mem0 Docs:** https://docs.mem0.ai/
- **Composio Docs:** https://docs.composio.dev/
- **OpenRouter Docs:** https://openrouter.ai/docs
- **Railway Docs:** https://docs.railway.app/
- **Render Docs:** https://render.com/docs

---

## 🔄 Rollback Plan

If deployment fails:

1. **Railway/Render:**
   - [ ] Revert to previous deployment
   - [ ] Check logs for errors
   - [ ] Fix issues locally
   - [ ] Redeploy

2. **VPS:**
   - [ ] Stop services
   - [ ] Restore from backup
   - [ ] Fix issues
   - [ ] Restart services

---

**Deployment Status:** ⏳ PENDING
**Next Action:** Choose platform and deploy!

🚀 **Good luck with your deployment!** 🚀
