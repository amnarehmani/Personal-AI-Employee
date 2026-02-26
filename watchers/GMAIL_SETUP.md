# Gmail Watcher - Setup and Authentication Guide

## Prerequisites Completed ✓

- [x] `credentials.json` created in project root
- [x] Google API libraries installed
- [x] Gmail Watcher script created

## First-Time Authentication

### Step 1: Run Authentication

Open a terminal and run:

```bash
cd "C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee"
python watchers/gmail_watcher.py --auth
```

### Step 2: Authorize in Browser

1. A browser window will open automatically
2. Sign in to your Google account
3. Click "Allow" to grant Gmail API access
4. The browser will show "Authentication successful"
5. A `token.json` file will be created in the project root

### Step 3: Verify Authentication

```bash
python watchers/gmail_watcher.py --test
```

Expected output:
```
[Test] Connected to: your-email@gmail.com
[Test] Unread emails: 5+
[Test] Connection test PASSED
```

---

## Running the Gmail Watcher

### Option 1: Run Continuously

```bash
python watchers/gmail_watcher.py
```

This will:
- Check Gmail every 2 minutes
- Create action files for new important emails
- Track processed emails to avoid duplicates

### Option 2: Run Once (for Scheduler)

```bash
python watchers/gmail_watcher.py --once
```

Use this with the scheduler for periodic checks.

### Option 3: Add to Windows Task Scheduler

```powershell
# Create scheduled task to run every 15 minutes
schtasks /create /tn "Gmail_Watcher" /tr "python watchers/gmail_watcher.py --once" /sc minute /mo 15 /ru "%USERNAME%"
```

---

## Configuration

### Edit Keywords (Optional)

Edit `watchers/gmail_watcher.py` and modify the `self.keywords` list:

```python
self.keywords = ['urgent', 'invoice', 'payment', 'asap', 'important', 'help']
```

### Add VIP Senders (Optional)

```python
self.vip_senders = ['boss@company.com', 'client@example.com']
```

### Change Check Interval

```bash
# Check every 5 minutes (300 seconds)
python watchers/gmail_watcher.py --interval 300
```

---

## How It Works

1. **Watcher runs** every 2 minutes
2. **Checks Gmail API** for unread emails
3. **Filters emails** by:
   - Important label
   - Keywords in subject
   - VIP senders
   - Has attachments
4. **Creates action file** in `AI_Employee_Vault/Needs_Action/`
5. **Tracks processed emails** to avoid duplicates
6. **Orchestrator detects** new action file
7. **Qwen Code processes** the email task

---

## Action File Format

When an email is detected, an action file is created:

```markdown
---
type: gmail_email
from: client@example.com
subject: Urgent: Invoice Request
received: 2026-02-26T10:30:00Z
priority: high
---

# Gmail Message

## From
client@example.com

## Subject
Urgent: Invoice Request

## Content
[Email body...]

## Suggested Actions
- [ ] Read and understand the email
- [ ] Draft appropriate response
- [ ] Take required action
```

---

## Troubleshooting

### "credentials.json not found"
- Ensure `credentials.json` is in project root
- File should contain your Google Cloud OAuth credentials

### "Token expired"
```bash
# Delete old token and re-authenticate
del token.json
python watchers/gmail_watcher.py --auth
```

### "No emails detected"
- Check if emails are marked as unread in Gmail
- Verify keywords match your emails
- Check Gmail spam folder

### "API quota exceeded"
- Gmail API has daily limits
- Wait 24 hours or reduce check frequency

---

## Testing

```bash
# Test connection
python watchers/gmail_watcher.py --test

# Show status
python watchers/gmail_watcher.py --status

# Clear processed cache
python watchers/gmail_watcher.py --clear-cache
```

---

*Gmail Watcher v0.1 - Silver Tier*
