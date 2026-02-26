# Quick Start Guide - Qwen Code Edition

## Get Started in 5 Minutes

### Step 1: Open the Vault in Obsidian

1. Open Obsidian
2. Click **File** → **Open Folder**
3. Select: `AI_Employee_Vault`

You should see:
- `Dashboard.md` - Main status page
- `Company_Handbook.md` - Rules for your AI
- `Business_Goals.md` - Your objectives

---

### Step 2: Start the FileSystem Watcher

Open a terminal and run:

```bash
cd "C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee"
python watchers/filesystem_watcher.py AI_Employee_Vault
```

**Keep this terminal open** - the watcher runs continuously.

You'll see:
```
2026-02-26 20:00:00 - FileSystemWatcher - INFO - Starting FileSystemWatcher
2026-02-26 20:00:00 - FileSystemWatcher - INFO - Vault path: AI_Employee_Vault
2026-02-26 20:00:00 - FileSystemWatcher - INFO - Check interval: 30s
```

---

### Step 3: Drop a Test File

In a **new terminal** or file explorer:

```bash
echo "Task: Draft a welcome email for a new client" > "AI_Employee_Vault/Inbox/test_task.txt"
```

**Wait 30 seconds** - the watcher will detect it.

You'll see in the watcher terminal:
```
2026-02-26 20:00:30 - FileSystemWatcher - INFO - New file detected: test_task.txt
2026-02-26 20:00:30 - FileSystemWatcher - INFO - Created action file: FILE_DROP_test_task_txt_...md
```

---

### Step 4: Process with Qwen Code

```bash
cd AI_Employee_Vault
qwen
```

**Prompt to give Qwen:**

```
Check the /Needs_Action folder for pending tasks.
Read each action file and create a plan to complete them.
Follow the rules in Company_Handbook.md.
Move completed tasks to /Done when finished.
```

---

### Step 5: Verify Results

In **Obsidian**, check:

1. **Needs_Action/** - Should be empty (task processed)
2. **Done/** - Should contain the completed task
3. **Dashboard.md** - Should show updated activity

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `python watchers/filesystem_watcher.py AI_Employee_Vault` | Start the file watcher |
| `python orchestrator.py AI_Employee_Vault` | Start orchestrator (auto-triggers Qwen) |
| `cd AI_Employee_Vault && qwen` | Run Qwen Code manually |
| `python test_watcher.py` | Test the watcher system |

---

## Workflow Summary

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Drop file in Inbox/                                      │
│         ↓                                                   │
│ 2. Watcher detects → Creates action file in Needs_Action/   │
│         ↓                                                   │
│ 3. Run: qwen                                                │
│         ↓                                                   │
│ 4. Qwen processes task → Moves to Done/                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

### Watcher doesn't detect files
- Ensure file is in `AI_Employee_Vault/Inbox/`
- Check watcher is running (look for log output)
- Wait 30 seconds (check interval)

### Qwen can't read vault
```bash
cd AI_Employee_Vault
qwen
```

### Action file not created
- Check watcher terminal for errors
- Verify file isn't hidden (no `.` prefix)
- Try running: `python test_watcher.py`

---

## Next Steps

After completing the test:

1. **Review Company_Handbook.md** - Understand the rules
2. **Update Business_Goals.md** - Set your objectives  
3. **Create real tasks** - Drop actual work files in Inbox/
4. **Run Qwen regularly** - Process tasks as they accumulate

---

*Powered by Qwen Code - AI Employee v0.1 (Bronze Tier)*
