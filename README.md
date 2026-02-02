# Trace Kernel (Pocket Agent) 🤖

**The Cognitive Operating System for the User.**

Trace Kernel is an intelligent, autonomous agent architected to bridge the gap between unstructured intent ("Do research") and deterministic execution ("Save to Notion"). It serves as a **Strategic Stack** component, treating every interaction as a "State Update" to your institutional memory.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Phase](https://img.shields.io/badge/Phase-2_Complete-green.svg)]()

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

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- API Keys: OpenRouter, Composio

### Installation

1. **Clone the Registry**
   ```bash
   git clone https://github.com/yourusername/pocket-agent.git
   cd pocket-agent
   ```

2. **Initialize the Factory**
   ```bash
   # Install Python deps (The Kernel)
   pip install -r requirements.txt
   
   # Install Bridge deps (The Senses)
   cd wpp-bridge && npm install && cd ..
   ```

3. **Configure Secrets**
   ```bash
   cp .env.example .env
   # Edit .env with your keys
   ```

4. **Ignite the Kernel**
   ```bash
   # Windows
   start_local.bat
   
   # Linux/VPS
   ./deploy_vps.sh
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
