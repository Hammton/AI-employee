# 🚀 Running PocketAgent with WPP Bridge (main_v2.py)

## Quick Start

### Prerequisites
1. Node.js installed (for WPP Bridge)
2. Python 3.8+ with dependencies installed
3. Environment variables configured in `.env`

### Required Environment Variables
```bash
# .env file
OPENROUTER_API_KEY=your_openrouter_key
COMPOSIO_API_KEY=your_composio_key
WPP_BRIDGE_URL=http://localhost:3001
PORT=8000
```

---

## Step-by-Step Setup

### 1. Start WPP Bridge (Terminal 1)
```bash
cd wpp-bridge
npm install  # First time only
npm start
```

**Expected Output:**
```
WPP Bridge Server running on port 3001
Waiting for QR code...
```

### 2. Scan QR Code
- Open the terminal running WPP Bridge
- Scan the QR code with WhatsApp mobile app
- Wait for "WhatsApp Connected!" message

### 3. Start PocketAgent (Terminal 2)
```bash
python main_v2.py
```

**Expected Output:**
```
    ╔═══════════════════════════════════════════════════════════╗
    ║                      POCKET AGENT                         ║
    ║              AI-Powered WhatsApp Assistant                ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  ARCHITECTURE:                                            ║
    ║    WhatsApp Web <-> WPP Bridge (Node.js) <-> PocketAgent  ║
    ║                                                           ║
    ║  SETUP:                                                   ║
    ║    1. Start WPP Bridge: cd wpp-bridge && npm start        ║
    ║    2. Start PocketAgent: python main.py                   ║
    ║    3. Scan QR code in WPP Bridge console                  ║
    ╚═══════════════════════════════════════════════════════════╝

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     🚀 Starting PocketAgent...
INFO:     🔌 Connecting to WPP Bridge at http://localhost:3001...
INFO:     ✅ WPP Bridge connected!
INFO:     ✅ PocketAgent Ready!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## Testing the Setup

### 1. Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{"status": "ok"}
```

### 2. WhatsApp Status
```bash
curl http://localhost:8000/whatsapp/status
```

**Expected Response:**
```json
{
  "ready": true,
  "connected": true
}
```

### 3. Send Test Message
Send a WhatsApp message to the connected number:
```
Hello!
```

**Expected Response:**
```
Hi! I'm PocketAgent, your AI assistant. How can I help you today?
```

---

## Common Issues & Solutions

### Issue 1: Port Already in Use
**Error:** `Address already in use: 8000`

**Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual process ID)
taskkill /PID <PID> /F

# Or use a different port
set PORT=8001
python main_v2.py
```

### Issue 2: WPP Bridge Not Connected
**Error:** `⏳ Waiting for WPP Bridge... (30/30)`

**Solution:**
1. Check WPP Bridge is running: `curl http://localhost:3001/status`
2. Verify WPP_BRIDGE_URL in `.env` is correct
3. Restart WPP Bridge and scan QR code again

### Issue 3: No Response to Messages
**Symptoms:** Messages sent but no reply

**Debug Steps:**
1. Check PocketAgent logs for errors
2. Verify webhook endpoint: `curl -X POST http://localhost:8000/whatsapp/incoming -H "Content-Type: application/json" -d '{"id":"test","from":"test@c.us","body":"test"}'`
3. Check WPP Bridge is forwarding messages to webhook
4. Verify OPENROUTER_API_KEY is set correctly

### Issue 4: Import Error
**Error:** `ModuleNotFoundError: No module named 'composio'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

## Architecture Overview

```
┌─────────────────┐
│  WhatsApp User  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WhatsApp Web   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WPP Bridge     │  (Node.js - Port 3001)
│  (wpp-bridge)   │
└────────┬────────┘
         │ HTTP POST
         ▼
┌─────────────────┐
│  PocketAgent    │  (Python FastAPI - Port 8000)
│  (main_v2.py)   │
│                 │
│  ┌───────────┐  │
│  │ Webhook   │  │  /whatsapp/incoming
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Per-User  │  │  get_kernel_for_user(chat_id)
│  │ Kernels   │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Composio  │  │  Tool execution
│  │ Session   │  │
│  └───────────┘  │
└─────────────────┘
```

---

## Per-User Kernel Isolation

### How It Works
Each WhatsApp user (identified by `chat_id`) gets their own kernel instance:

```python
# User A sends message
chat_id_a = "+1234567890@c.us"
kernel_a = get_kernel_for_user(chat_id_a)  # Creates new kernel

# User B sends message
chat_id_b = "+0987654321@c.us"
kernel_b = get_kernel_for_user(chat_id_b)  # Creates new kernel

# User A sends another message
kernel_a_again = get_kernel_for_user(chat_id_a)  # Reuses existing kernel
assert kernel_a is kernel_a_again  # Same instance!
```

### Benefits
- ✅ Each user has isolated tool connections
- ✅ Privacy protected (users can't see each other's data)
- ✅ Unique auth URLs per user
- ✅ Efficient memory usage (kernels reused)

---

## API Endpoints

### GET /
Health check with WhatsApp status
```bash
curl http://localhost:8000/
```

### GET /health
Simple health check
```bash
curl http://localhost:8000/health
```

### GET /whatsapp/status
Get WhatsApp connection status
```bash
curl http://localhost:8000/whatsapp/status
```

### POST /whatsapp/incoming
Webhook for incoming messages (called by WPP Bridge)
```bash
curl -X POST http://localhost:8000/whatsapp/incoming \
  -H "Content-Type: application/json" \
  -d '{
    "id": "msg123",
    "from": "+1234567890@c.us",
    "body": "Hello!",
    "type": "chat"
  }'
```

### POST /whatsapp/send
Send a text message
```bash
curl -X POST http://localhost:8000/whatsapp/send \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890@c.us",
    "message": "Hello from PocketAgent!"
  }'
```

### POST /whatsapp/send/image
Send an image
```bash
curl -X POST http://localhost:8000/whatsapp/send/image \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+1234567890@c.us",
    "base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "caption": "Test image",
    "filename": "test.png"
  }'
```

### GET /connect/{app_name}
Generate OAuth URL for a Composio app
```bash
curl http://localhost:8000/connect/asana
```

### POST /add-app/{app_name}
Add a Composio app to the agent
```bash
curl -X POST http://localhost:8000/add-app/asana
```

---

## Monitoring & Logs

### Log Levels
- `INFO`: Normal operations
- `WARNING`: Non-critical issues
- `ERROR`: Critical errors

### Key Log Messages
```
🚀 Starting PocketAgent...
🔌 Connecting to WPP Bridge...
✅ WPP Bridge connected!
✅ PocketAgent Ready!
📩 Processing message from Alice: Hello!
🔧 Creating new kernel for user: +1234567890@c.us
🎨 Image command detected. Prompt: a cat
✅ Image generated! Size: 123456 bytes
```

---

## Stopping the Server

### Graceful Shutdown
Press `CTRL+C` in the terminal running `main_v2.py`

**Expected Output:**
```
^C
INFO:     Shutting down
INFO:     👋 PocketAgent shutdown complete.
INFO:     Finished server process [12345]
```

### Force Stop (if needed)
```bash
# Windows
taskkill /F /IM python.exe

# Linux/Mac
pkill -9 python
```

---

## Production Deployment

### Railway
1. Create new project
2. Add environment variables
3. Deploy from GitHub
4. Set start command: `python main_v2.py`

### Render
1. Create new Web Service
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main_v2.py`
5. Add environment variables

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main_v2.py"]
```

---

## Testing Per-User Isolation

Run the test suite:
```bash
python test_main_v2_per_user.py
```

**Expected Output:**
```
============================================================
TEST: Per-User Kernel Isolation (main_v2.py)
============================================================

1️⃣ Creating kernels for 3 users...
   ✅ Kernel created for +1234567890@c.us
   ✅ Kernel created for +0987654321@c.us
   ✅ Kernel created for +1122334455@c.us

2️⃣ Verifying kernel uniqueness...
   ✅ All kernels are unique instances

3️⃣ Testing kernel reuse (same user requests again)...
   ✅ Kernel reused for +1234567890@c.us
   ✅ Kernel reused for +0987654321@c.us
   ✅ Kernel reused for +1122334455@c.us

4️⃣ Generating auth URLs for each user...
   ✅ +1234567890@c.u... → https://connect.composio.dev/link/lk_5Fiv7WCnRNrD...
   ✅ +0987654321@c.u... → https://connect.composio.dev/link/lk_wHmRkSiAOnGa...
   ✅ +1122334455@c.u... → https://connect.composio.dev/link/lk_h1WD2Cb3JCxI...

5️⃣ Verifying auth URLs are unique...
   ✅ All auth URLs are unique!

============================================================
✅ ALL TESTS PASSED!
============================================================
```

---

## Support

### Documentation
- `MAIN_V2_PER_USER_FIX.md` - Per-user kernel fix details
- `PER_USER_FIX_SUMMARY.md` - Original fix for main.py
- `FIX_SUMMARY.md` - Session-based authentication
- `kernel.py` - Core kernel implementation

### Troubleshooting
1. Check logs for error messages
2. Verify environment variables are set
3. Test WPP Bridge connection
4. Run test suite to verify setup
5. Check API endpoints are responding

---

**Last Updated:** January 31, 2026  
**Status:** ✅ Production Ready  
**Architecture:** WPP Bridge + FastAPI Webhook
