# PocketAgent - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Connect Anchor Browser (Web Browsing)
```bash
python connect_anchor_browser.py
```
- Copy the auth URL
- Visit it in your browser
- Complete the OAuth flow
- Done! ✅

### Step 2: Restart the Server
```bash
# Kill existing process on port 8000
taskkill /F /PID <process_id>

# Start fresh
python main_v2.py
```

### Step 3: Test Web Browsing
Send this via WhatsApp:
```
Visit https://example.com and tell me what you see
```

The agent will now browse the web for you! 🌐

## 📱 What You Can Do Right Now

### Email Management
```
Show me my unread emails
Reply to the email from John
Send an email to sarah@example.com about the meeting
```

### Task Management (Asana)
```
List my Asana projects
Create a task "Review Q1 report" in project "Marketing"
Show me my tasks due this week
```

### Calendar
```
What's on my calendar today?
Schedule a meeting with John tomorrow at 2pm
Show me my free slots this week
```

### Web Browsing
```
Visit https://news.ycombinator.com and summarize the top stories
Search for "best restaurants in Nairobi"
Take a screenshot of https://example.com
```

### Document Creation
```
Create a Google Doc with a project proposal
Write a brief about our Q1 results in Google Docs
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Required
OPENROUTER_API_KEY=your_key_here
COMPOSIO_API_KEY=your_key_here

# Optional - Customize models
LLM_MODEL=google/gemini-2.0-flash-exp
VISION_MODEL=google/gemini-2.0-flash-exp
IMAGE_MODEL=google/gemini-2.5-flash-image
```

### Available Models (via OpenRouter)
- `google/gemini-2.0-flash-exp` - Fast, cheap, good
- `anthropic/claude-3.5-sonnet` - Best quality
- `openai/gpt-4-turbo` - OpenAI's best
- `meta-llama/llama-3.1-70b` - Open source
- And 100+ more!

## 📊 Architecture Overview

```
WhatsApp Message
    ↓
WPP Bridge (Node.js) - Port 3001
    ↓
PocketAgent (Python) - Port 8000
    ↓
Kernel (LangChain + Composio)
    ↓
┌─────────────┬──────────────┬─────────────┐
│  OpenRouter │   Composio   │   Memory    │
│  (AI Model) │   (Tools)    │   (JSON)    │
└─────────────┴──────────────┴─────────────┘
```

## 🔌 Connected Apps

Check what's connected:
```bash
python check_user_connections.py
```

Connect new apps:
```bash
python connect_anchor_browser.py  # Web browsing
# Or ask the agent: "Connect Google Sheets"
```

## 🐛 Troubleshooting

### "No connected account found"
**Problem:** App not connected
**Solution:** 
```bash
python connect_anchor_browser.py
# Visit the auth URL
```

### "Port 8000 already in use"
**Problem:** Server already running
**Solution:**
```bash
netstat -ano | findstr :8000
taskkill /F /PID <process_id>
```

### "Tools not loading"
**Problem:** Auto-detection failed
**Solution:**
```bash
# Check logs in server output
# Restart server
python main_v2.py
```

## 📈 Next Steps

### Add More Channels (30 min)
```bash
pip install python-telegram-bot
# Create telegram bot
# Add to main_v2.py
```

### Add Memory to Kernel (15 min)
```python
# In kernel.py
from add_memory_system import ConversationMemory

class AgentKernel:
    def __init__(self, user_id):
        self.memory = ConversationMemory(user_id)
    
    def run(self, goal):
        # Load context
        context = self.memory.get_context_summary()
        
        # Process with context
        result = self.agent_executor.invoke(...)
        
        # Save to memory
        self.memory.save_message("user", goal)
        self.memory.save_message("assistant", result)
        
        return result
```

### Deploy to Cloudflare (1 day)
See `MOLTBOT_COMPARISON_AND_ROADMAP.md` for detailed guide.

## 🎯 Pro Tips

1. **Use specific models for specific tasks**
   - Fast tasks: `gemini-2.0-flash-exp`
   - Complex reasoning: `claude-3.5-sonnet`
   - Vision: `gemini-2.0-flash-exp`

2. **Connect apps as needed**
   - Don't connect everything at once
   - Connect when you need a feature
   - Reduces tool loading time

3. **Monitor costs**
   - OpenRouter dashboard shows usage
   - Gemini Flash is very cheap
   - Claude Sonnet is expensive but best

4. **Test locally first**
   - Use test scripts before WhatsApp
   - Check logs for errors
   - Verify connections

## 📚 Documentation

- `ACHIEVEMENT_SUMMARY.md` - What we built
- `MOLTBOT_COMPARISON_AND_ROADMAP.md` - Feature comparison
- `ANCHOR_BROWSER_SETUP.md` - Web browsing setup
- `GET_TOOLS_SOLUTION_SUMMARY.md` - Tool loading details

## 🆘 Get Help

1. Check server logs: `python main_v2.py`
2. Test connections: `python check_user_connections.py`
3. Verify tools: `python check_loaded_tools.py`
4. Read error messages carefully

## ✅ Checklist

- [ ] Anchor Browser connected
- [ ] Server running on port 8000
- [ ] WPP Bridge running on port 3001
- [ ] WhatsApp QR code scanned
- [ ] Test message sent
- [ ] Web browsing tested
- [ ] Tools working

## 🎉 You're Ready!

Your AI agent is now:
- ✅ Managing emails
- ✅ Scheduling meetings
- ✅ Creating documents
- ✅ Managing tasks
- ✅ Browsing the web
- ✅ Remembering conversations

**Start chatting and let your AI assistant do the work!** 🚀
