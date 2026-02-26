# AI Employee - Qwen Code Bronze Tier

## Complete System Overview

This is your **Personal AI Employee** powered by **Qwen Code** and **Obsidian**.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Employee System                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. INPUT: Drop files in Inbox/                                │
│         ↓                                                       │
│  2. FileSystem Watcher (filesystem_watcher.py)                 │
│     - Monitors Inbox/ every 30s                                │
│     - Creates action files in Needs_Action/                    │
│         ↓                                                       │
│  3. Orchestrator (orchestrator.py)                             │
│     - Monitors Needs_Action/ every 30s                         │
│     - Triggers Qwen Code automatically                         │
│         ↓                                                       │
│  4. Qwen Code                                                   │
│     - Reads action files                                       │
│     - Creates plans in Plans/                                  │
│     - Executes tasks                                           │
│     - Moves completed to Done/                                 │
│     - Updates Dashboard.md                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start (3 Steps)

### Step 1: Open Vault in Obsidian

1. Open **Obsidian**
2. Click **File** → **Open Folder**
3. Select: `AI_Employee_Vault`

You should see:
- `Dashboard.md` - Main status page
- `Company_Handbook.md` - Rules for your AI
- `Business_Goals.md` - Your objectives
- Folders: `Inbox/`, `Needs_Action/`, `Done/`, etc.

---

### Step 2: Start the Orchestrator

Open a terminal and run:

```bash
cd "C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee"
python orchestrator.py AI_Employee_Vault
```

**Keep this terminal open** - the orchestrator runs continuously.

You'll see:
```
[Orchestrator] Vault path: AI_Employee_Vault
[Orchestrator] Check interval: 30s
[Orchestrator] Qwen Code: qwen
[Orchestrator] Monitoring: Needs_Action

[Orchestrator] Starting AI Employee Orchestrator
[Orchestrator] Press Ctrl+C to stop
```

---

### Step 3: Drop a Test File

In a **new terminal** or file explorer:

```bash
echo "Task: Draft a welcome email for a new client" > "AI_Employee_Vault/Inbox/test_task.txt"
```

**Wait up to 60 seconds** (30s for watcher + 30s for orchestrator).

You'll see in the orchestrator terminal:
```
[Orchestrator] New task detected: FILE_DROP_test_task_txt_...md
[Orchestrator] Triggering Qwen Code for 1 task(s)...
```

Qwen Code will then process the task automatically.

---

## Commands Reference

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `python orchestrator.py AI_Employee_Vault` | Start full automation | **Recommended** - Run this |
| `python watchers/filesystem_watcher.py AI_Employee_Vault` | Start watcher only | Manual Qwen processing |
| `cd AI_Employee_Vault && qwen` | Run Qwen Code manually | When not using orchestrator |
| `python test_watcher.py` | Test watcher system | Before first use |
| `python test_orchestrator.py` | Test orchestrator system | Before first use |

---

## Complete Workflow Example

### Scenario: Client sends invoice request

**1. Create the request file:**
```bash
echo "Client: Acme Corp
Service: Website Redesign
Amount: $2,500
Due Date: March 15, 2026
Notes: First milestone completed" > "AI_Employee_Vault/Inbox/invoice_acme.txt"
```

**2. System automatically processes:**

```
Terminal output (orchestrator running):
─────────────────────────────────────────────
[Orchestrator] New task detected: invoice_acme.txt
[Orchestrator] Triggering Qwen Code for 1 task(s)...
[Orchestrator] Running: qwen

# Qwen Code output appears here
# - Reading action file...
# - Creating plan...
# - Executing task...
# - Updating Dashboard...

[Orchestrator] Qwen Code processing complete
[Orchestrator] Dashboard updated
─────────────────────────────────────────────
```

**3. Check results in Obsidian:**
- `Dashboard.md` - Shows new activity
- `Plans/` - Contains the plan Qwen created
- `Done/` - Contains the completed task file
- `Invoices/` - Contains the generated invoice

---

## System Components

### 1. FileSystem Watcher (`watchers/filesystem_watcher.py`)

**Purpose:** Monitors `Inbox/` folder for new files

**What it does:**
- Scans every 30 seconds
- Detects new files (by hash)
- Creates action files in `Needs_Action/`
- Copies original files for reference

**Action file format:**
```markdown
---
type: file_drop
source_file: invoice_acme.txt
file_size: 512 bytes
received: 2026-02-26T20:00:00
priority: normal
status: pending
---

# File Drop for Processing

## Source
- **Original File:** `invoice_acme.txt`
- **Size:** 512 bytes

## Suggested Actions
- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done
```

---

### 2. Orchestrator (`orchestrator.py`)

**Purpose:** Coordinates the entire workflow

**What it does:**
- Monitors `Needs_Action/` every 30 seconds
- Detects new action files
- Builds comprehensive prompts for Qwen Code
- Automatically triggers Qwen Code
- Updates `Dashboard.md` with activity
- Logs all events to `Logs/`

**Log format (in `Logs/YYYY-MM-DD.jsonl`):**
```json
{
  "timestamp": "2026-02-26T20:00:00",
  "event": "qwen_triggered",
  "details": {
    "task_count": 1,
    "tasks": ["FILE_DROP_test_txt_...md"]
  }
}
```

---

### 3. Qwen Code

**Purpose:** Reasoning engine that processes tasks

**What it does:**
- Reads action files from `Needs_Action/`
- Checks `Company_Handbook.md` for rules
- Creates plans in `Plans/`
- Executes tasks
- Moves completed files to `Done/`
- Updates `Dashboard.md`

---

## File Structure

```
Personal-AI-Employee/
├── AI_Employee_Vault/           # Obsidian vault
│   ├── Dashboard.md             # Status dashboard
│   ├── Company_Handbook.md      # Rules of engagement
│   ├── Business_Goals.md        # Objectives
│   ├── Inbox/                   # Drop files here
│   ├── Needs_Action/            # Action files (auto-created)
│   ├── Done/                    # Completed tasks
│   ├── Plans/                   # Qwen's plans
│   ├── Pending_Approval/        # Awaiting approval
│   ├── Logs/                    # Activity logs
│   └── Accounting/              # Financial records
│
├── watchers/
│   ├── base_watcher.py          # Base class for watchers
│   └── filesystem_watcher.py    # File monitoring
│
├── orchestrator.py              # Main orchestrator
├── test_watcher.py              # Watcher tests
├── test_orchestrator.py         # Orchestrator tests
├── BRONZE_README.md             # Main documentation
├── QUICKSTART_QWEN.md           # Quick start guide
└── HOW_TO_RUN.md                # This file
```

---

## Testing the System

### Run All Tests

```bash
# Test watcher
python test_watcher.py

# Test orchestrator
python test_orchestrator.py
```

**Expected output:**
```
[PASS] ALL TESTS PASSED
```

---

## Troubleshooting

### Orchestrator doesn't start
```bash
# Check Python version
python --version  # Should be 3.13+

# Check file exists
dir orchestrator.py
```

### Watcher doesn't detect files
- Ensure files are in `AI_Employee_Vault/Inbox/`
- Check orchestrator terminal for output
- Wait 30-60 seconds (check intervals)

### Qwen Code not triggered
```bash
# Check Qwen is installed
qwen --version

# If not found, install or add to PATH
```

### Action files pile up in Needs_Action/
- Check orchestrator is running
- Check Qwen Code is working: `cd AI_Employee_Vault && qwen`
- Review logs: `dir Logs/`

---

## Daily Usage

### Morning
1. Open Obsidian vault
2. Review `Dashboard.md`
3. Start orchestrator: `python orchestrator.py AI_Employee_Vault`

### During Day
- Drop files in `Inbox/` as tasks come in
- Orchestrator processes automatically
- Check `Done/` folder for completed tasks

### Evening
- Review `Dashboard.md` for activity summary
- Check `Logs/` for detailed activity
- Stop orchestrator: `Ctrl+C` in terminal

---

## Best Practices

1. **Keep orchestrator running** during work hours
2. **Review Dashboard.md** daily
3. **Check Pending_Approval/** for items needing your input
4. **Archive old logs** monthly (move to archive folder)
5. **Update Company_Handbook.md** as rules evolve

---

## Next Steps (Silver Tier)

To upgrade beyond Bronze:
1. Add Gmail Watcher
2. Add WhatsApp Watcher  
3. Implement MCP servers for external actions
4. Add scheduling (cron/Task Scheduler)
5. Create approval workflow UI

---

*Powered by Qwen Code - AI Employee v0.1 (Bronze Tier)*
