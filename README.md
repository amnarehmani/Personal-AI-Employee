# Personal AI Employee

> **Your life and business on autopilot. Local-first, agent-driven, human-in-the-loop.**

A hackathon project building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI employee that manages personal and business affairs 24/7 using **Qwen Code** and **Obsidian**.

![Tier](https://img.shields.io/badge/Tier-Silver-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🏆 Hackathon Status

| Tier | Status | Description |
|------|--------|-------------|
| **Bronze** | ✅ Complete | Foundation with FileSystem Watcher |
| **Silver** | ✅ Complete | Functional Assistant with Gmail + LinkedIn |
| Gold | 🔄 Planned | Autonomous Employee |
| Platinum | 📋 Planned | Always-On Cloud + Local |

---

## ✨ Features

### Bronze Tier (Complete)
- ✅ **Obsidian Vault** with Dashboard, Company Handbook, Business Goals
- ✅ **FileSystem Watcher** - Monitors drop folder for new files
- ✅ **Qwen Code Integration** - Reads/writes to vault
- ✅ **Folder Structure** - `/Inbox`, `/Needs_Action`, `/Done`, `/Plans`, `/Pending_Approval`
- ✅ **Orchestrator** - Coordinates watchers and Qwen Code
- ✅ **Dashboard Updater** - Real-time status updates

### Silver Tier (Complete)
- ✅ **Gmail Watcher** - Monitors Gmail for important emails
- ✅ **LinkedIn Integration** - Post drafts and browser automation
- ✅ **Email MCP** - Send emails via SMTP
- ✅ **Approval Workflow** - Human-in-the-loop for sensitive actions
- ✅ **Plan Creator** - Structured multi-step task plans
- ✅ **Scheduler** - Cron/Task Scheduler integration
- ✅ **Daily Briefing** - Automated morning reports

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PERSONAL AI EMPLOYEE                         │
├─────────────────────────────────────────────────────────────────┤
│  EXTERNAL SOURCES                                               │
│  Gmail │ WhatsApp │ LinkedIn │ Bank APIs │ File Drops          │
├─────────────────────────────────────────────────────────────────┤
│  PERCEPTION LAYER (Watchers)                                    │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Gmail Watcher│ │LinkedIn Watch│ │File Watcher  │            │
│  └──────┬───────┘ └──────┬───────┘ └──────┬───────┘            │
└─────────┼────────────────┼────────────────┼────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OBSIDIAN VAULT (Memory/GUI)                  │
│  Dashboard.md │ Company_Handbook.md │ Business_Goals.md         │
│  /Inbox │ /Needs_Action │ /Done │ /Plans │ /Pending_Approval   │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                              │
│                    QWEN CODE                                    │
│         Read → Think → Plan → Write → Request Approval          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ACTION LAYER (MCP Servers)                   │
│  Email MCP │ Browser/Playwright │ Approval Workflow             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
Personal-AI-Employee/
├── AI_Employee_Vault/           # Obsidian vault
│   ├── Dashboard.md             # Real-time status dashboard
│   ├── Company_Handbook.md      # Rules of engagement
│   ├── Business_Goals.md        # Objectives and targets
│   ├── Inbox/                   # Drop folder for files
│   ├── Needs_Action/            # Action files (auto-created)
│   ├── Done/                    # Completed tasks
│   ├── Plans/                   # Multi-step task plans
│   ├── Pending_Approval/        # Awaiting human approval
│   ├── Approved/                # Approved actions
│   ├── Logs/                    # Activity logs
│   └── Accounting/              # Financial records
│
├── .qwen/skills/                # Qwen Agent Skills
│   ├── browsing-with-playwright/
│   ├── approval-workflow/
│   ├── plan-creator/
│   ├── email-mcp/
│   ├── gmail-watcher/
│   ├── linkedin-posting/
│   └── mcp-server/
│
├── watchers/                    # Watcher scripts
│   ├── base_watcher.py          # Base class for all watchers
│   ├── filesystem_watcher.py    # File system monitor
│   ├── gmail_watcher.py         # Gmail monitor
│   ├── linkedin_watcher.py      # LinkedIn poster
│   ├── linkedin_post_interactive.py
│   └── linkedin_quick_post.py
│
├── scripts/
│   ├── scheduler.py             # Task scheduler
│   └── tasks/
│       └── daily_briefing.py    # Daily briefing generator
│
├── orchestrator.py              # Main orchestrator
├── update_dashboard.py          # Dashboard updater
├── test_watcher.py              # Watcher tests
└── test_orchestrator.py         # Orchestrator tests
```

---

## 🚀 Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| [Python](https://python.org) | 3.13+ | Watcher scripts |
| [Obsidian](https://obsidian.md) | v1.10.6+ | Knowledge base |
| [Qwen Code](https://claude.com/product/claude-code) | Active | Reasoning engine |
| [Node.js](https://nodejs.org) | v24+ LTS | MCP servers |

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Personal-AI-Employee
   ```

2. **Install Python dependencies**
   ```bash
   pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
   ```

3. **Open Obsidian Vault**
   - Open Obsidian
   - File → Open Folder → `AI_Employee_Vault`

4. **Configure Gmail (Optional)**
   - Place `credentials.json` in project root
   - Run: `python watchers/gmail_watcher.py --auth`

### First Run

```bash
# Test the watcher
python test_watcher.py

# Start the orchestrator
python orchestrator.py AI_Employee_Vault

# In another terminal, start Qwen Code
cd AI_Employee_Vault
qwen
```

---

## 📖 Usage Guide

### 1. File Drop Workflow

```bash
# Drop a file in Inbox
echo "Process this document" > AI_Employee_Vault/Inbox/document.txt

# Watcher creates action file in Needs_Action/
# Orchestrator triggers Qwen Code
# Qwen processes and moves to Done/
```

### 2. Gmail Monitoring

```bash
# First-time authentication
python watchers/gmail_watcher.py --auth

# Test connection
python watchers/gmail_watcher.py --test

# Run continuously
python watchers/gmail_watcher.py
```

### 3. LinkedIn Posting

**Method 1: Quick Post**
```bash
python watchers/linkedin_quick_post.py
```

**Method 2: Create Draft**
```bash
python watchers/linkedin_watcher.py --post --content "Your post content #hashtag"
# Then move file from Pending_Approval/ to Approved/
```

### 4. Daily Briefing

```bash
# Generate morning briefing
python scripts/tasks/daily_briefing.py

# Or schedule it
python scripts/scheduler.py run
```

---

## 🧪 Testing

```bash
# Test watcher
python test_watcher.py

# Test orchestrator
python test_orchestrator.py

# Verify Playwright server
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

---

## 📋 Configuration

### Gmail Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project and enable Gmail API
3. Download `credentials.json` to project root
4. Run authentication: `python watchers/gmail_watcher.py --auth`

### Environment Variables (.env)

```bash
# Email Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# LinkedIn (if using API)
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
```

---

## 🎯 Silver Tier Requirements Coverage

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ | Complete |
| 2 | Two or more Watcher scripts | ✅ | FileSystem + Gmail |
| 3 | Automatically Post on LinkedIn | ✅ | LinkedIn Watcher |
| 4 | Plan.md creation | ✅ | Plan Creator skill |
| 5 | One working MCP server | ✅ | Email + Playwright |
| 6 | Human-in-the-loop approval | ✅ | Approval Workflow |
| 7 | Basic scheduling | ✅ | Scheduler script |
| 8 | All as Agent Skills | ✅ | All documented |

**Coverage: 8/8 (100%)** ✅

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [BRONZE_README.md](BRONZE_README.md) | Bronze tier documentation |
| [HOW_TO_RUN.md](HOW_TO_RUN.md) | Complete running guide |
| [QUICKSTART_QWEN.md](QUICKSTART_QWEN.md) | Quick start for Qwen Code |
| [SILVER_TIER_PLAN.md](SILVER_TIER_PLAN.md) | Silver tier implementation plan |
| [SILVER_TIER_SKILLS.md](SILVER_TIER_SKILLS.md) | Skills documentation |
| [AUTHENTICATE_GMAIL.md](AUTHENTICATE_GMAIL.md) | Gmail authentication guide |

---

## 🔧 Commands Reference

### Watchers
```bash
python watchers/filesystem_watcher.py AI_Employee_Vault
python watchers/gmail_watcher.py --auth
python watchers/gmail_watcher.py --test
python watchers/gmail_watcher.py
```

### LinkedIn
```bash
python watchers/linkedin_watcher.py --post --content "Your post"
python watchers/linkedin_quick_post.py
```

### Orchestrator & Scheduler
```bash
python orchestrator.py AI_Employee_Vault
python scripts/scheduler.py run
python scripts/scheduler.py setup-windows
```

### Dashboard
```bash
python update_dashboard.py AI_Employee_Vault
python scripts/tasks/daily_briefing.py
```

---

## 🤝 Contributing

This is a hackathon project. Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

---

## 📄 License

MIT License - See LICENSE file for details.

---

## 🙏 Acknowledgments

- [Personal AI Employee Hackathon](https://github.com/Personal-AI-Employee-Hackathon)
- [Qwen Code](https://claude.com/product/claude-code)
- [Obsidian](https://obsidian.md)
- [Playwright MCP](https://github.com/playwright-community/playwright-mcp)

---

## 📞 Support

For issues or questions:
1. Check existing documentation
2. Review test files for examples
3. Open an issue on GitHub

---

*Built with ❤️ for the Personal AI Employee Hackathon 0*

**Current Version:** Silver Tier v0.2  
**Last Updated:** February 2026
