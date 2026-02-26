# Personal AI Employee

## Project Overview

This is a **hackathon project** for building a "Digital FTE" (Full-Time Equivalent) — an autonomous AI employee that manages personal and business affairs 24/7. The architecture is **local-first, agent-driven, and human-in-the-loop**.

**Core Concept:** An AI agent powered by **Claude Code** (reasoning engine) and **Obsidian** (knowledge base/dashboard) that proactively handles tasks like email triage, WhatsApp monitoring, bank transaction auditing, and social media posting.

### Architecture Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Brain** | Claude Code | Reasoning engine for task planning and execution |
| **Memory/GUI** | Obsidian | Local Markdown vault serving as dashboard and long-term memory |
| **Senses** | Python Watchers | Background scripts monitoring Gmail, WhatsApp, filesystems |
| **Hands** | MCP Servers | Model Context Protocol servers for external actions (browser, email, payments) |
| **Persistence** | Ralph Wiggum Loop | Stop hook pattern keeping Claude working until tasks complete |

### Key Features

- **Watcher Architecture:** Lightweight Python scripts continuously monitor inputs and create actionable `.md` files in `/Needs_Action`
- **Human-in-the-Loop:** Sensitive actions require approval via file movement (`/Pending_Approval` → `/Approved`)
- **Monday Morning CEO Briefing:** Autonomous weekly audit generating revenue reports, bottleneck analysis, and proactive suggestions
- **Tiered Achievement Levels:** Bronze (foundation) → Silver (functional) → Gold (autonomous) → Platinum (always-on cloud + local)

## Project Structure

```
Personal-AI-Employee/
├── Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md  # Main blueprint
├── skills-lock.json          # Skill dependencies registry
├── .qwen/skills/
│   └── browsing-with-playwright/
│       ├── SKILL.md          # Skill documentation
│       ├── references/
│       │   └── playwright-tools.md  # MCP tool reference
│       └── scripts/
│           ├── mcp-client.py  # Universal MCP client (HTTP + stdio)
│           ├── start-server.sh
│           ├── stop-server.sh
│           └── verify.py      # Server health check
```

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Primary reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base & dashboard |
| Python | 3.13+ | Watcher scripts & orchestration |
| Node.js | v24+ LTS | MCP servers |
| GitHub Desktop | Latest | Version control |

### Playwright MCP Server

The project includes a browser automation skill using Playwright MCP.

```bash
# Start the browser server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Stop the server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh
```

### MCP Client Usage

The `mcp-client.py` script connects to MCP servers:

```bash
# List available tools (HTTP transport)
python mcp-client.py list --url http://localhost:8808

# Call a tool
python mcp-client.py call -u http://localhost:8808 -t browser_navigate \
  -p '{"url": "https://example.com"}'

# Emit tool schemas as markdown
python mcp-client.py emit --url http://localhost:8808
```

### Ralph Wiggum Loop (Persistence Pattern)

Keep Claude working autonomously until task completion:

```bash
# Start a Ralph loop
/ralph-loop "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10
```

## Development Conventions

### File-Based Communication

Agents communicate via the Obsidian vault using standardized folders:

| Folder | Purpose |
|--------|---------|
| `/Inbox` | Raw incoming items |
| `/Needs_Action` | Items requiring processing |
| `/In_Progress/<agent>/` | Claimed tasks (prevents double-work) |
| `/Pending_Approval` | Actions awaiting human approval |
| `/Approved` | Approved actions ready for execution |
| `/Done` | Completed tasks |
| `/Plans` | Multi-step task plans |
| `/Briefings` | CEO briefing reports |

### Watcher Script Pattern

All watchers follow the `BaseWatcher` template:

```python
class BaseWatcher(ABC):
    def check_for_updates(self) -> list:
        """Return list of new items to process"""
        pass

    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder"""
        pass

    def run(self):
        """Main loop with error handling"""
```

### Action File Schema

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-01-07T10:30:00Z
priority: high
status: pending
---

## Email Content
<message snippet>

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
```

## Key Workflows

### 1. Email Processing
1. Gmail Watcher detects unread important emails
2. Creates `.md` file in `/Needs_Action`
3. Claude reads, plans response
4. For sensitive actions: writes to `/Pending_Approval`
5. Human moves to `/Approved`
6. Email MCP sends response

### 2. Weekly Business Audit
1. Scheduled trigger (Sunday night)
2. Claude reads `Business_Goals.md`, `Tasks/Done`, `Bank_Transactions.md`
3. Generates "Monday Morning CEO Briefing" with:
   - Revenue summary
   - Bottleneck analysis
   - Proactive suggestions (e.g., unused subscriptions)

### 3. Social Media Posting
1. Claude drafts post based on business goals
2. Writes draft to `/Pending_Approval`
3. Human approves
4. Browser MCP or Social MCP publishes

## References

- [Playwright MCP Tools](.qwen/skills/browsing-with-playwright/references/playwright-tools.md) - Complete tool reference for browser automation
- [Ralph Wiggum Pattern](https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum) - Persistence loop implementation

## Hackathon Tiers

| Tier | Time | Deliverables |
|------|------|--------------|
| **Bronze** | 8-12h | Obsidian vault, 1 watcher, basic folder structure |
| **Silver** | 20-30h | 2+ watchers, MCP integration, approval workflow |
| **Gold** | 40+h | Full integration, Odoo accounting, Ralph loop, audit logging |
| **Platinum** | 60+h | Cloud deployment, domain specialization, A2A sync |
