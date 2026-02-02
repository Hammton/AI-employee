# Pocket Agent 🤖

An intelligent WhatsApp AI agent powered by LangChain, Composio, and OpenRouter. Execute tasks, manage integrations, and automate workflows directly from WhatsApp.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

## ✨ Features

- **🔗 Multi-Integration Support**: Connect Gmail, Google Calendar, Google Sheets, Google Docs, Notion, Asana, Slack, GitHub, and more
- **⚡ Immediate Execution**: No permission asking - the agent executes tasks immediately
- **🧠 Intelligent Memory**: Powered by Mem0 for context-aware conversations
- **🎨 Image Generation**: Create images using AI models
- **🌐 Web Browsing**: Browse the web with Anchor Browser integration
- **💻 Autonomous Execution**: Execute shell commands and local file operations
- **🎯 Skills System**: Create and manage reusable agent skills
- **📱 WhatsApp Interface**: Interact naturally via WhatsApp messages

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ (for WhatsApp bridge)
- OpenRouter API key
- Composio API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/pocket-agent.git
cd pocket-agent
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Node.js dependencies (for WhatsApp bridge)**
```bash
cd wpp-bridge
npm install
cd ..
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENROUTER_API_KEY=your_openrouter_key
COMPOSIO_API_KEY=your_composio_key
LLM_MODEL=google/gemini-3-flash-preview
```

5. **Start the agent**
```bash
# Windows
start_local.bat

# Linux/Mac
chmod +x start_local.sh
./start_local.sh
```

This will:
- Start the WhatsApp Bridge (Node.js) on port 3001
- Start the AI Agent (Python) on port 8000
- Open a window with QR code for WhatsApp

6. **Scan QR code** with WhatsApp to connect

## 📖 Documentation

- **[Quick Start Guide](docs/QUICK_START_GUIDE.md)** - Get up and running in 5 minutes
- **[Proactive Agent Guide](docs/PROACTIVE_AGENT_GUIDE.md)** - Learn about proactive behavior
- **[Skills System](docs/SKILLS_SYSTEM_DESIGN.md)** - Create custom agent skills
- **[Autonomous Execution](docs/AUTONOMOUS_EXECUTION.md)** - Enable local command execution
- **[Mem0 Integration](docs/MEM0_INTEGRATION_GUIDE.md)** - Set up intelligent memory
- **[Anchor Browser Setup](docs/ANCHOR_BROWSER_SETUP.md)** - Enable web browsing

## 🎯 Usage Examples

### Create a Google Doc
```
User: create a google doc
Agent: ✅ Created! Here's your document: [link]
```

### Send an Email
```
User: send an email to john@example.com saying "Meeting at 3pm"
Agent: ✅ Email sent!
```

### Create a Task in Asana
```
User: create a task "Review PR" in asana
Agent: ✅ Task created in Asana!
```

### Generate an Image
```
User: generate an image of a sunset over mountains
Agent: ✅ [Generated image]
```

## 🔧 Configuration

### Supported Models

**LLM Models** (via OpenRouter):
- `google/gemini-3-flash-preview` (default, fast)
- `anthropic/claude-3.5-sonnet`
- `openai/gpt-4-turbo`

**Image Models**:
- `google/gemini-2.5-flash-image` (default)
- `black-forest-labs/flux-1.1-pro`

### Supported Integrations

- **Productivity**: Gmail, Google Calendar, Google Drive, Google Docs, Google Sheets
- **Project Management**: Asana, Notion, GitHub
- **Communication**: Slack
- **Web**: Anchor Browser (web browsing and automation)

## 🏗️ Architecture

The system consists of two main components that work together:

### 1. WhatsApp Bridge (Node.js)
- Handles WhatsApp Web connection
- Manages QR code authentication
- Forwards messages to Python agent
- Runs on port 3001

### 2. AI Agent (Python)
- Processes messages with LLM
- Executes tools via Composio
- Manages user context and memory
- Runs on port 8000

```
┌─────────────────┐
│   WhatsApp      │
│   (User Input)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  WPP Bridge     │  ← Port 3001 (Node.js)
│  (Node.js)      │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│   Main Agent    │  ← Port 8000 (Python)
│   (main.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent Kernel   │
│  (kernel.py)    │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌──────────┐
│LangChain│ │ Composio │
│ (LLM)   │ │ (Tools)  │
└─────────┘ └──────────┘
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://langchain.com/) - LLM framework
- [Composio](https://composio.dev/) - Tool integration platform
- [OpenRouter](https://openrouter.ai/) - LLM API gateway
- [WPPConnect](https://wppconnect.io/) - WhatsApp Web API

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/pocket-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/pocket-agent/discussions)

## 🗺️ Roadmap

- [ ] Voice message support
- [ ] Multi-user support with user isolation
- [ ] Web dashboard for management
- [ ] More integration support (Trello, Linear, etc.)
- [ ] Custom skill marketplace
- [ ] Docker deployment support

---

Made with ❤️ by the Pocket Agent team
