# PocketAgent Cloud Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAILWAY                                   │
│  ┌─────────────────────────┐   ┌─────────────────────────────┐  │
│  │   🧠 pocket-agent       │   │   📱 wpp-bridge             │  │
│  │   (Python/FastAPI)      │◄──│   (Node.js/WPPConnect)      │  │
│  │   Port: 8000            │   │   Port: 3001                │  │
│  │                         │──►│   + Chromium                │  │
│  │   - AI Logic            │   │   - WhatsApp Connection     │  │
│  │   - Composio Tools      │   │   - Session Persistence     │  │
│  │   - Message Processing  │   │   - QR Code Generation      │  │
│  └─────────────────────────┘   └─────────────────────────────┘  │
│            ▲                              │ Volume: wpp-tokens  │
│            │                              ▼                      │
│            │                   ┌─────────────────────────┐      │
│            │                   │  Persistent Storage     │      │
│            │                   │  (WhatsApp Session)     │      │
│            │                   └─────────────────────────┘      │
└────────────│────────────────────────────────────────────────────┘
             │
     ┌───────┴───────┐
     │  WhatsApp     │
     │  (Your Phone) │
     └───────────────┘
```

## Deployment Options

### Option 1: Railway (Recommended) ⭐

Railway supports both services with persistent volumes for WhatsApp sessions.

#### Step 1: Create Railway Project

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd pocket-agent
railway init
```

#### Step 2: Deploy WPP Bridge First

```bash
cd wpp-bridge
railway up

# Set environment variables
railway variables set PYTHON_CALLBACK_URL=<python-service-internal-url>
railway variables set PORT=3001

# Add volume for session persistence
railway volume create wpp-tokens --mount /app/tokens
```

#### Step 3: Deploy Python Backend

```bash
cd ..
railway up

# Set environment variables
railway variables set OPENROUTER_API_KEY=your_key
railway variables set COMPOSIO_API_KEY=your_key
railway variables set LLM_MODEL=openai/gpt-4o
railway variables set IMAGE_MODEL=google/gemini-2.5-flash-image-preview
railway variables set WPP_BRIDGE_URL=<wpp-bridge-internal-url>
railway variables set USER_PHONE=your_phone_number
```

#### Step 4: Connect Services

In Railway Dashboard:
1. Go to your project
2. Click on `pocket-agent` service
3. Go to "Networking" → "Private Networking"
4. Copy the internal URL (e.g., `pocket-agent.railway.internal:8000`)
5. Set this as `PYTHON_CALLBACK_URL` in wpp-bridge

### Option 2: Docker Compose (Self-Hosted)

For VPS deployment (DigitalOcean, Hetzner, etc.):

```bash
# Clone and configure
git clone <your-repo>
cd pocket-agent

# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=your_key
COMPOSIO_API_KEY=your_key
LLM_MODEL=openai/gpt-4o
IMAGE_MODEL=google/gemini-2.5-flash-image-preview
USER_PHONE=your_phone
EOF

# Deploy
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Render.com

Similar to Railway but uses `render.yaml`:

```yaml
# render.yaml
services:
  - type: web
    name: pocket-agent
    runtime: docker
    dockerfilePath: ./Dockerfile.python
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: WPP_BRIDGE_URL
        value: https://wpp-bridge.onrender.com

  - type: web
    name: wpp-bridge
    runtime: docker
    dockerContext: ./wpp-bridge
    dockerfilePath: ./Dockerfile
    disk:
      name: wpp-tokens
      mountPath: /app/tokens
      sizeGB: 1
```

## Environment Variables

### pocket-agent (Python)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ | OpenRouter API key |
| `COMPOSIO_API_KEY` | ✅ | Composio API key for tools |
| `LLM_MODEL` | ❌ | Default: `openai/gpt-4o` |
| `VISION_MODEL` | ❌ | Default: same as LLM_MODEL |
| `IMAGE_MODEL` | ❌ | Default: `google/gemini-2.5-flash-image-preview` |
| `WPP_BRIDGE_URL` | ✅ | Internal URL of wpp-bridge |
| `USER_PHONE` | ❌ | Your phone number for owner commands |

### wpp-bridge (Node.js)

| Variable | Required | Description |
|----------|----------|-------------|
| `PYTHON_CALLBACK_URL` | ✅ | Internal URL of pocket-agent |
| `PORT` | ❌ | Default: `3001` |

## First-Time Setup (QR Code Scan)

1. Deploy both services
2. Access wpp-bridge logs: `railway logs -s wpp-bridge`
3. Look for the QR code URL or scan from logs
4. Scan with WhatsApp on your phone
5. Session is saved to volume (persists across restarts)

## Scaling Considerations

### For Multi-Tenant (SaaS)

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRACE PLATFORM                               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    API GATEWAY                               │ │
│  │              (Auth + Tenant Routing)                         │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                            │                                     │
│       ┌────────────────────┼────────────────────┐               │
│       ▼                    ▼                    ▼               │
│  ┌─────────┐          ┌─────────┐          ┌─────────┐         │
│  │ Tenant1 │          │ Tenant2 │          │ Tenant3 │         │
│  │ Agent   │          │ Agent   │          │ Agent   │         │
│  └─────────┘          └─────────┘          └─────────┘         │
│       │                    │                    │               │
│       ▼                    ▼                    ▼               │
│  ┌─────────┐          ┌─────────┐          ┌─────────┐         │
│  │ WPP     │          │ WPP     │          │ WPP     │         │
│  │ Bridge1 │          │ Bridge2 │          │ Bridge3 │         │
│  └─────────┘          └─────────┘          └─────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

For multi-tenant, consider:
- **Modal.com** for serverless agent execution (per-request billing)
- **Redis** for session state sharing
- **PostgreSQL** for user/tenant management

## Cost Estimation (Railway)

| Resource | Usage | Cost/Month |
|----------|-------|------------|
| pocket-agent | ~256MB RAM, always-on | ~$5 |
| wpp-bridge | ~512MB RAM, always-on | ~$10 |
| Volume (1GB) | Session storage | ~$0.25 |
| **Total** | | **~$15-20** |

## Troubleshooting

### WhatsApp Not Connecting
```bash
# Check wpp-bridge logs
railway logs -s wpp-bridge

# Look for QR code or auth errors
```

### Messages Not Processing
```bash
# Check pocket-agent logs
railway logs -s pocket-agent

# Verify WPP_BRIDGE_URL is correct
railway variables -s pocket-agent
```

### Session Lost After Restart
- Ensure volume is properly mounted
- Check if `/app/tokens` directory exists in container
- Verify volume wasn't deleted during redeployment

## Recommended: Railway Monorepo Setup

Create a `railway.json` in root for full project deployment:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

Then deploy with:
```bash
railway up --detach
```

---

## Option 4: Modal.com (Serverless Agents) ⚡

For **pay-per-second** agent execution ($0.04 per task):

### Setup

```bash
# Install Modal CLI
pip install modal

# Login
modal setup

# Create secrets in Modal dashboard
# - openrouter-secret: OPENROUTER_API_KEY
# - composio-secret: COMPOSIO_API_KEY

# Deploy
modal deploy modal_agent.py
```

### Usage

Modal provides HTTP endpoints for triggering agents:

```bash
# Execute a task
curl -X POST https://your-app--execute-task.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "goal": "Send email to john@example.com about the meeting",
    "apps": ["gmail", "calendar"]
  }'

# Vision task
curl -X POST https://your-app--execute-vision.modal.run \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://...",
    "prompt": "Analyze this product image"
  }'
```

### Cost Comparison

| Platform | Model | Cost/Month (100 tasks/day) |
|----------|-------|---------------------------|
| Railway | Always-on | ~$15-20 |
| Modal | Per-request | ~$4-8 |
| Render | Always-on | ~$14-25 |

---

## CI/CD: GitHub Actions

Automatic deployment on push to `main`:

### Setup

1. **Add secrets to GitHub repo:**
   - `OPENROUTER_API_KEY`
   - `COMPOSIO_API_KEY`
   - `RAILWAY_TOKEN` (from Railway dashboard)

2. **Push to main branch:**
   ```bash
   git add .
   git commit -m "Deploy PocketAgent"
   git push origin main
   ```

3. **GitHub Actions will:**
   - Run tests
   - Build Docker images
   - Deploy to Railway/Render

See `.github/workflows/deploy.yml` for configuration.

---

## Quick Reference

| File | Purpose |
|------|---------|
| `Dockerfile.python` | Python backend container |
| `wpp-bridge/Dockerfile` | WhatsApp bridge container |
| `docker-compose.yml` | Local/VPS deployment |
| `railway.toml` | Railway configuration |
| `render.yaml` | Render.com blueprint |
| `modal_agent.py` | Serverless agent execution |
| `.github/workflows/deploy.yml` | CI/CD pipeline |
