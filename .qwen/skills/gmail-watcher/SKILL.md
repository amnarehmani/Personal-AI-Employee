---
name: gmail-watcher
description: |
  Monitor Gmail for new important emails and create action files.
  Uses Gmail API to watch for unread, important emails and emails from VIP contacts.
  Creates action files in Needs_Action folder for Qwen Code to process.
---

# Gmail Watcher

Monitor Gmail and create actionable tasks from new emails.

## Quick Start

### 1. Setup Gmail API

```bash
# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib

# Enable Gmail API at: https://console.cloud.google.com/apis/library/gmail.googleapis.com

# Download credentials.json and place in project root
```

### 2. Run Watcher

```bash
python .qwen/skills/gmail-watcher/scripts/gmail-watcher.py
```

### 3. Or Add to Scheduler

```bash
# Add to scripts/scheduler.py tasks
python scripts/scheduler.py run  # Runs every 30 minutes
```

---

## Configuration

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` to project root
6. First run will create `token.json` for refresh

### Environment Variables

```bash
# .env file
GMAIL_WATCH_INTERVAL=300      # Check every 5 minutes
GMAIL_MAX_RESULTS=10            # Max emails per check
GMAIL_KEYWORDS=urgent,invoice,payment,asap  # Keywords to watch
GMAIL_VIP_SENDERS=client@example.com,boss@company.com
```

---

## Watcher Behavior

### Emails That Trigger Action Files

1. **Unread + Important** (Gmail's important marker)
2. **From VIP senders** (configured list)
3. **Contains keywords** (urgent, invoice, payment, ASAP)
4. **Has attachments** (potential documents to process)

### Action File Format

```markdown
---
type: gmail_email
from: client@example.com
subject: Urgent: Invoice Request
received: 2026-02-26T10:30:00Z
message_id: 18e4f1234567890a
priority: high
status: pending
---

# Gmail Message

## From
client@example.com

## Subject
Urgent: Invoice Request

## Received
2026-02-26 10:30:00

## Content
Hi,

Could you please send me the invoice for the recent project?

Thanks,
Client

## Suggested Actions
- [ ] Reply to sender
- [ ] Generate and send invoice
- [ ] Mark as processed
```

---

## Script Usage

### Run Watcher

```bash
python .qwen/skills/gmail-watcher/scripts/gmail-watcher.py
```

### Test Connection

```bash
python gmail-watcher.py --test
```

### Check Processed IDs

```bash
python gmail-watcher.py --status
```

### Clear Processed Cache

```bash
python gmail-watcher.py --clear-cache
```

---

## Integration with Orchestrator

The orchestrator automatically:
1. Detects new action files created by Gmail Watcher
2. Triggers Qwen Code to process emails
3. Qwen drafts replies or takes actions
4. Files moved to Done when complete

---

## Workflow

```
1. Gmail Watcher runs (every 5 min)
         ↓
2. Checks Gmail API for new emails
         ↓
3. Filters: unread + important/VIP/keywords
         ↓
4. Creates action file in Needs_Action/
         ↓
5. Orchestrator detects → Triggers Qwen Code
         ↓
6. Qwen processes email → Moves to Done/
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication error | Re-run to refresh token |
| No emails detected | Check Gmail labels/filters |
| API quota exceeded | Wait and retry (daily limit) |
| Credentials error | Verify credentials.json |

---

*Gmail Watcher Skill v0.1 - Silver Tier*
