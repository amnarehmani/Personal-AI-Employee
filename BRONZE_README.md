# AI Employee - Bronze & Silver Tier

A **Personal AI Employee** implementation using Qwen Code and Obsidian. 

**Bronze Tier:** Foundation (Complete ✓)
**Silver Tier:** Functional Assistant (Complete ✓)

## Overview

This project implements a local-first, agent-driven AI employee that:
- Monitors a drop folder for new files
- Creates actionable tasks in an Obsidian vault
- Uses Qwen Code for reasoning and task processing
- Follows human-in-the-loop approval patterns

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  File Drop      │────▶│  FileSystem      │────▶│  Obsidian Vault │
│  (Inbox)        │     │  Watcher         │     │  (Memory/GUI)   │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
                                                          ▼
                                                 ┌─────────────────┐
                                                 │   Qwen Code     │
                                                 │  (Reasoning)    │
                                                 └─────────────────┘
```

## Project Structure

```
Personal-AI-Employee/
├── AI_Employee_Vault/          # Obsidian vault
│   ├── Dashboard.md            # Real-time status dashboard
│   ├── Company_Handbook.md     # Rules of engagement
│   ├── Business_Goals.md       # Objectives and targets
│   ├── Inbox/                  # Drop folder for files
│   ├── Needs_Action/           # Action files created by watcher
│   ├── Done/                   # Completed tasks
│   ├── Plans/                  # Multi-step task plans
│   ├── Pending_Approval/       # Awaiting human approval
│   ├── Approved/               # Approved actions
│   ├── Rejected/               # Rejected actions
│   ├── Logs/                   # Activity logs
│   ├── Accounting/             # Financial records
│   └── Briefings/              # CEO briefings
├── watchers/
│   ├── base_watcher.py         # Abstract base class for watchers
│   └── filesystem_watcher.py   # File system monitoring script
├── test_watcher.py             # Test script
└── BRONZE_README.md            # This file
```

## Quick Start

### Prerequisites

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.13+ | Watcher scripts |
| Obsidian | v1.10.6+ | Knowledge base |
| Qwen Code | Active subscription | Reasoning engine |

### Installation

1. **Clone or download this repository**

2. **Open the vault in Obsidian**
   ```
   File → Open Folder → AI_Employee_Vault
   ```

3. **Verify Python version**
   ```bash
   python --version  # Should be 3.13 or higher
   ```

### Running the FileSystem Watcher

**Option 1: Run once (test)**
```bash
python test_watcher.py
```

**Option 2: Run watcher continuously (manual processing)**
```bash
python watchers/filesystem_watcher.py AI_Employee_Vault
# Then manually run: cd AI_Employee_Vault && qwen
```

**Option 3: Run orchestrator (automatic processing) - RECOMMENDED**
```bash
python orchestrator.py AI_Employee_Vault
```

The **orchestrator** automatically:
- Checks the `Needs_Action` folder every 30 seconds
- Detects new action files created by the watcher
- Triggers Qwen Code to process tasks automatically
- Updates Dashboard.md with activity
- Logs all events to `/Logs/`

### Using Qwen Code

Once action files are created:

```bash
cd AI_Employee_Vault
qwen
```

Then prompt Qwen Code:
```
Check the /Needs_Action folder and process any pending tasks.
Create a plan for each task and move completed items to /Done.
```

## How It Works

### 1. File Drop
Place any file in `AI_Employee_Vault/Inbox/`

### 2. Watcher Detection
The `filesystem_watcher.py` script:
- Scans the Inbox folder every 30 seconds
- Calculates file hash to detect duplicates
- Identifies new files
- Creates action files in `Needs_Action/`

### 3. Orchestrator Detection
The `orchestrator.py` script:
- Monitors `Needs_Action/` for new action files
- Detects new tasks every 30 seconds
- Builds a comprehensive prompt for Qwen Code
- Triggers Qwen Code automatically

### 4. Qwen Processing
Qwen Code reads the action file, understands the task, and:
- Creates a plan in `/Plans`
- Executes actions (with approval if needed)
- Moves completed tasks to `/Done`
- Updates `Dashboard.md`

## Testing

Run the test suite:
```bash
python test_watcher.py
```

Expected output:
```
[PASS] ALL TESTS PASSED

Next steps:
1. Run watcher: python watchers/filesystem_watcher.py AI_Employee_Vault
2. Drop files in: AI_Employee_Vault/Inbox/
3. Check action files in: AI_Employee_Vault/Needs_Action/
```

## Bronze Tier Deliverables Checklist

- [x] **Obsidian vault** with Dashboard.md and Company_Handbook.md
- [x] **One working Watcher script** (FileSystem Watcher)
- [x] **Claude Code integration** - reads/writes to vault
- [x] **Basic folder structure**: /Inbox, /Needs_Action, /Done
- [ ] **Agent Skills** - Convert AI functionality to Claude Agent Skills

## Usage Examples

### Example 1: Process Invoice Request

**Step 1: Create invoice request file**
```bash
echo "Client: Acme Corp
Service: Website Redesign
Amount: $2,500
Due Date: March 15, 2026" > "AI_Employee_Vault/Inbox/invoice_acme.txt"
```

**Step 2: Start the orchestrator (if not already running)**
```bash
python orchestrator.py AI_Employee_Vault
```

**What happens automatically:**
1. Watcher detects the file in Inbox
2. Watcher creates action file in `Needs_Action/`
3. Orchestrator detects the new action file
4. Orchestrator triggers Qwen Code
5. Qwen creates invoice and moves task to `/Done/`

### Example 2: Daily Task Review

**Manual processing (without orchestrator):**
```bash
cd AI_Employee_Vault
qwen "Review all pending tasks in Needs_Action and create a prioritized plan"
```

**Automatic processing (with orchestrator running):**
- Just drop files in `Inbox/`
- Orchestrator handles the rest automatically

## Configuration

### Adjust Watcher Check Interval

Edit `watchers/filesystem_watcher.py`:
```python
watcher = FileSystemWatcher(str(vault_path), check_interval=60)  # Check every 60 seconds
```

### Add Custom Watcher

Create a new watcher by extending `BaseWatcher`:
```python
from base_watcher import BaseWatcher

class MyWatcher(BaseWatcher):
    def check_for_updates(self) -> list:
        # Your detection logic here
        pass
    
    def create_action_file(self, item) -> Path:
        # Your action file creation logic here
        pass
```

## Troubleshooting

### Watcher doesn't detect files
- Ensure files are placed in `AI_Employee_Vault/Inbox/`
- Check watcher is running: look for log output
- Verify file isn't hidden (no `.` prefix)

### Action files not created
- Check `Needs_Action` folder exists
- Verify write permissions
- Check watcher logs for errors

### Orchestrator doesn't trigger Qwen Code
- Check orchestrator is running: `python orchestrator.py AI_Employee_Vault`
- Verify Qwen Code is installed: `qwen --version`
- Check logs in `/Logs/` folder for errors

### Qwen Code can't read vault
- Run Qwen from vault directory: `cd AI_Employee_Vault && qwen`
- Or use `--cwd` flag if available: `qwen --cwd AI_Employee_Vault`

## Next Steps (Silver Tier)

To upgrade to Silver Tier:
1. Add Gmail Watcher or WhatsApp Watcher
2. Implement MCP server for email sending
3. Create approval workflow
4. Add scheduling via cron/Task Scheduler
5. Implement Plan.md creation by Qwen Code

## Resources

- [Hackathon Blueprint](../Personal%20AI%20Employee%20Hackathon%200_%20Building%20Autonomous%20FTEs%20in%202026.md)
- [Qwen Code Documentation](https://claude.com/product/claude-code)
- [Obsidian Documentation](https://help.obsidian.md)
- [Agent Skills Documentation](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)

## License

This project is part of the Personal AI Employee Hackathon 0.

---

*Built for Personal AI Employee Hackathon 0 - Bronze Tier*
