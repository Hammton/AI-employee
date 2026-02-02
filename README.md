# Trace Kernel (Pocket Agent) 🤖

**The Cognitive Operating System for the User.**

Trace Kernel is an intelligent, autonomous agent architected to bridge the gap between unstructured intent ("Do research") and deterministic execution ("Save to Notion"). It serves as a **Strategic Stack** component, treating every interaction as a "State Update" to your institutional memory.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Phase](https://img.shields.io/badge/Phase-2_Complete-green.svg)]()

## 🤖 What is Moltbot?

**Moltbot** is an AI agent chatbot that can use various software apps and online tools. It accepts commands in plain English to perform tasks like editing documents, sending emails, or building apps. Moltbot is open-source and popular among AI researchers, developers, and tech enthusiasts.

**Key Features**:
- Uses software apps and online tools autonomously
- Accepts plain English commands
- Open-source architecture
- Can edit documents, send emails, build apps

**Moltbook**: A social network where 10,000+ Moltbots chat with each other, demonstrating the power of autonomous AI agents working together.

**Note**: This project (Trace Kernel/Pocket Agent) is inspired by Moltbot's autonomous execution philosophy but focuses on production-ready, secure implementations with proper error handling and user control.

## ✨ Core Capabilities (The Refinery)

- **🧠 Trace Kernel**: A monolithic cognitive engine that routes decisions based on intent intensity.
- **🛠️ Skill Engine (Phase 2)**: Learns from your workflows. Say *"Do X, then Y"*, and it creates a permanent, reusable skill (`SKILL.md`).
- **🔗 Hyper-Connected**: Native integrations for **Gmail, Calendar, Notion, Sheets, Docs, Asana, Slack, GitHub**.
- **⚡ "Magic in Public"**: Immediate execution with "Safe Mode" for risky commands.
- **📱 Sensory Layer**: Full WhatsApp two-way capability (Voice, Image, Text) via `wpp-bridge`.
- **🌐 Anchor Browser**: Autonomous web navigation for "Deep Research" tasks.

## 🏗️ Architecture: The Strategic Stack

The system is designed as a **Decision Graph** rather than a simple chatbot.

```ascii
┌──────────────────────┐       ┌──────────────────────┐
│  User / Leadership   │──────►│    Sensory Layer     │
│  (WhatsApp Input)    │       │  (WPP Bridge Node.js)│
└──────────────────────┘       └──┬───────────────────┘
                                  │ "State Update" (JSON)
                                  ▼
┌─────────────────────────────────────────────────────┐
│             TRACE KERNEL (Python / FastAPI)         │
│                                                     │
│  ┌───────────────┐   ┌──────────────────────┐       │
│  │ Context Stack │◄──┤ Intent/Decision Loop │       │
│  │ (Mem0/Vector) │   └──────────┬───────────┘       │
│  └───────────────┘              │                   │
│                                 ▼                   │
│  ┌────────────────────┐   ┌──────────────────────┐  │
│  │   Skill Engine     │   │   Composio Tools     │  │
│  │  (Registry/YAML)   │   │   (Action Layer)     │  │
│  └─────────┬──────────┘   └──────────┬───────────┘  │
│            │                         │              │
│            ▼                         ▼              │
└────────────┼─────────────────────────┼──────────────┘
             │                         │
      ┌──────▼──────┐           ┌──────▼──────┐
      │ File System │           │ External API│
      │ (Skills DB) │           │ (SaaS Stack)│
      └─────────────┘           └─────────────┘
```

### Components
1.  **Sensory Layer (Port 3001)**: Node.js bridge handling real-time WhatsApp encryption/decryption and media handling.
2.  **The Kernel (Port 8000)**: Python-based "Brain" that manages the **Ontology**. It doesn't just "chat"; it "refines" crude data into structured outcomes.
3.  **Skill Registry**: A file-system based database of `SKILL.md` files. This is the **Institutional Memory**—if the server dies, the skills remain.

## 🚀 Installation Guide

Complete step-by-step setup. Follow each step in order.

---

### Step 1: Prerequisites

Ensure you have the following installed:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.12+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Git | Any | `git --version` |

**Required API Keys:**
- [OpenRouter API Key](https://openrouter.ai/keys) - For LLM access
- [Composio API Key](https://app.composio.dev/settings) - For tool integrations

---

### Step 2: Clone the Repository

```bash
git clone https://github.com/yourusername/pocket-agent.git
cd pocket-agent
```

---

### Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4: Install Node.js Dependencies (WhatsApp Bridge)

```bash
cd wpp-bridge
npm install
cd ..
```

---

### Step 5: Configure Environment Variables

Rename the example file:

```bash
# Windows:
ren .env.example .env

# Linux/Mac:
mv .env.example .env
```

Open `.env` and add your API keys:

```env
# Required API Keys
OPENROUTER_API_KEY=sk-or-v1-your-key-here
COMPOSIO_API_KEY=your-composio-key-here

# Server Configuration
PORT=8000
WPP_BRIDGE_URL=http://localhost:3001
WPP_BRIDGE_PORT=3001

# AI Model (default works well)
LLM_MODEL=google/gemini-2.5-flash
```

---

### Step 6: Set Up Composio (Tool Integrations)

Composio powers all the app integrations (Gmail, Calendar, Notion, etc.).

**1. Create a Composio Account:**
- Go to [https://app.composio.dev](https://app.composio.dev)
- Sign up with Google or email
- Copy your API key from Settings → API Keys

**2. Add API Key to `.env`:**
```env
COMPOSIO_API_KEY=your-composio-key-here
```

**3. Connect Your Apps:**

When you first use the agent, it will detect which apps you need and provide authentication links:

```
User: Send an email to john@example.com
Agent: I tried to use GMAIL but you're not connected yet. 
       Please authenticate here: https://app.composio.dev/auth/gmail/...
```

**→ Click the link → Authorize → Return to WhatsApp and say:**

```
User: I have authorized
Agent: ✅ Gmail connected! Sending email now...
```

The agent will then proceed with your original request.

**Pre-connect apps (optional):**
You can also connect apps directly in Composio dashboard:
- Go to [https://app.composio.dev/apps](https://app.composio.dev/apps)
- Click on Gmail, Google Calendar, Notion, etc.
- Click "Connect" and authorize

---

### Step 7: Start the WhatsApp Bridge (Terminal 1)

Open a **new terminal window** and run:

```bash
cd pocket-agent/wpp-bridge
node index.js
```

**Expected output:**
```
[WPP] Starting WhatsApp Bridge on port 3001...
[WPP] Waiting for QR code...
[WPP] ████████████████████████████
[WPP] █ QR CODE WILL APPEAR HERE █
[WPP] ████████████████████████████
```

**→ Scan the QR code with your phone** (WhatsApp > Settings > Linked Devices > Link a Device)

---

### Step 8: Start the Backend Server (Terminal 2)

Open a **second terminal window** and run:

```bash
cd pocket-agent
python main_v2.py
```

**Expected output:**
```
INFO:     Started server on http://0.0.0.0:8000
INFO:     Application startup complete.
🤖 Trace Kernel initialized. Ready to receive messages.
```

---

### Step 9: Verify Connection

Send a message to yourself on WhatsApp. If working correctly:
1. You'll see the message logged in Terminal 2
2. The agent will respond automatically

**Test message:** `What can you do?`

---

## 🛑 Stopping the Servers

- **WhatsApp Bridge:** Press `Ctrl+C` in Terminal 1
- **Backend Server:** Press `Ctrl+C` in Terminal 2

---

## 🔄 Restarting After System Reboot

```bash
# Terminal 1: Start WhatsApp Bridge
cd pocket-agent/wpp-bridge
node index.js

# Terminal 2: Start Backend Server
cd pocket-agent
python main_v2.py
```

## 🎯 "Magic in Public" Usage

### 1. The Legacy Lifter (Document Automation)
Transform raw logic into premium documents.
```
User: Create a google doc called "Strategy_v1" with a plan for the Refinery launch.
Agent: ✅ Doc "Strategy_v1" created at [link].
```

### 2. The Skill Creator (Phase 2)
Teach the agent a new workflow instantly.
```
User: Research "Agentic Workflows", save a summary to Notion, and email it to hammton@example.com
Agent: 🧠 Executing and Learning...
Agent: ✅ Workflow complete. I've saved this as a new skill: 'research-notion-email'.
```

### 3. Deep Research
```
User: Browse moltapp.ai and tell me their pricing model.
Agent: 🌐 Browsing... Found pricing tiers [Start, Pro, Enterprise]...
```

## 🤝 Contributing to the Stack

1.  **Fork** the Refinery.
2.  **Create** your feature branch (`git checkout -b feat/new-module`).
3.  **Commit** your updates (`git commit -m 'feat: added neural graph'`).
4.  **Push** to the origin.

## 📝 License

MIT License. Built for the **Open Future**.

---
*Architected for the "Billion Dollar Database" initiative.*
