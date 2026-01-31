# ⚡ Quick Start - PocketAgent with Per-User Isolation

## 🚀 Choose Your Architecture

### Option 1: WPP Bridge (Recommended) ✅
**File:** `main_v2.py`  
**Best for:** Production, stability, multiple users

```bash
# Terminal 1: Start WPP Bridge
cd wpp-bridge && npm start

# Terminal 2: Start PocketAgent
python main_v2.py
```

### Option 2: Direct Playwright
**File:** `main.py`  
**Best for:** Development, testing, single user

```bash
python main.py
```

---

## ✅ Per-User Isolation Status

| Architecture | Status | User ID Source | Test File |
|--------------|--------|----------------|-----------|
| main.py (Playwright) | ✅ Fixed | sender_name | test_per_user_kernel.py |
| main_v2.py (WPP Bridge) | ✅ Fixed | chat_id | test_main_v2_per_user.py |

---

## 🧪 Test Per-User Isolation

```bash
# Test main.py
python test_per_user_kernel.py

# Test main_v2.py
python test_main_v2_per_user.py
```

**Expected:** ✅ All tests passing

---

## 🔑 Environment Variables

Create `.env` file:
```bash
OPENROUTER_API_KEY=your_key_here
COMPOSIO_API_KEY=your_key_here
WPP_BRIDGE_URL=http://localhost:3001  # For main_v2.py only
PORT=8000
```

---

## 📱 Test with WhatsApp

### 1. Connect a Tool
```
/connect asana
```

**Expected:** Unique auth URL per user
```
https://connect.composio.dev/link/lk_XXXXX
```

### 2. List Tools
```
/tools
```

### 3. Generate Image
```
/image a futuristic city
```

### 4. Get Help
```
/help
```

---

## 🎯 Key Features

✅ **Per-User Isolation** - Each WhatsApp user gets their own kernel  
✅ **Unique Auth URLs** - Secure links per user  
✅ **Tool Isolation** - Users can't see each other's data  
✅ **Memory Efficient** - Kernels are reused  
✅ **Production Ready** - Tested and documented  

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `SESSION_SUMMARY.md` | Complete session overview |
| `MAIN_V2_PER_USER_FIX.md` | Technical fix details (WPP Bridge) |
| `PER_USER_FIX_SUMMARY.md` | Technical fix details (Playwright) |
| `RUN_MAIN_V2.md` | Complete setup guide |
| `QUICK_START.md` | This file |

---

## 🆘 Common Issues

### Port Already in Use
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Missing Dependencies
```bash
pip install -r requirements.txt
cd wpp-bridge && npm install
```

### WPP Bridge Not Connected
1. Check WPP Bridge is running
2. Scan QR code
3. Verify WPP_BRIDGE_URL in .env

---

## ✨ What's New

### Before Fix ❌
- All users shared `default_user` entity
- Tool connections mixed between users
- Privacy violation

### After Fix ✅
- Each user gets unique entity_id
- Tool connections isolated per user
- Privacy protected
- Unique auth URLs per user

---

## 🎉 You're Ready!

Both architectures now have per-user kernel isolation working correctly. Choose the one that fits your needs and start building!

**Questions?** Check the documentation files above.

---

**Last Updated:** January 31, 2026  
**Status:** ✅ Production Ready
