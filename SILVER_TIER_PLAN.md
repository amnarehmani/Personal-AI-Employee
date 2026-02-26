# Silver Tier Skills Plan

## Silver Tier Requirements (from Hackathon Document)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | All Bronze requirements | ✅ Complete | Already built |
| 2 | Two or more Watcher scripts | ⏳ Pending | Gmail Watcher + WhatsApp Watcher |
| 3 | Automatically Post on LinkedIn | ⏳ Pending | LinkedIn MCP Server + Skill |
| 4 | Claude reasoning loop that creates Plan.md | ⏳ Pending | Plan Creator Skill |
| 5 | One working MCP server for external action | ⏳ Pending | Email MCP Server |
| 6 | Human-in-the-loop approval workflow | ⏳ Pending | Approval Workflow Skill |
| 7 | Basic scheduling via cron/Task Scheduler | ⏳ Pending | Scheduler Script |
| 8 | All AI functionality as Agent Skills | ⏳ Pending | Create all as Qwen Skills |

---

## Skills Required for Silver Tier

### 1. **email-mcp** (NEW)
**Purpose:** Send emails via Gmail/SMTP

**Tools:**
- `send_email` - Send an email
- `draft_email` - Create email draft
- `search_emails` - Search inbox

**Files to Create:**
```
.qwen/skills/email-mcp/
├── SKILL.md
├── scripts/
│   ├── mcp-server.py      # Email MCP server
│   ├── start-server.sh
│   └── stop-server.sh
└── references/
    └── email-tools.md
```

**Dependencies:**
- Python `smtplib` (built-in)
- Gmail API credentials OR SMTP credentials

---

### 2. **gmail-watcher** (NEW)
**Purpose:** Monitor Gmail for new important emails

**Triggers:**
- Unread important emails
- Emails from VIP contacts
- Emails with urgent keywords

**Files to Create:**
```
watchers/
├── gmail_watcher.py       # Gmail watcher script
└── requirements.txt       # Python dependencies
```

**Dependencies:**
- `google-api-python-client`
- `google-auth-httplib2`
- `google-auth-oauthlib`

---

### 3. **linkedin-posting** (NEW)
**Purpose:** Post updates to LinkedIn automatically

**Tools:**
- `create_post` - Create a LinkedIn post
- `schedule_post` - Schedule post for later
- `get_analytics` - Get post analytics

**Files to Create:**
```
.qwen/skills/linkedin-posting/
├── SKILL.md
├── scripts/
│   ├── mcp-server.py      # LinkedIn MCP server
│   ├── start-server.sh
│   └── stop-server.sh
└── references/
    └── linkedin-api.md
```

**Dependencies:**
- LinkedIn API credentials
- `requests` library

**Note:** LinkedIn API requires business account and app approval

---

### 4. **approval-workflow** (NEW)
**Purpose:** Human-in-the-loop approval system

**Tools:**
- `request_approval` - Create approval request file
- `check_approval_status` - Check if approved
- `get_pending_approvals` - List pending approvals

**Files to Create:**
```
.qwen/skills/approval-workflow/
├── SKILL.md
└── scripts/
    └── approval-manager.py
```

**Workflow:**
```
1. Qwen detects action requiring approval
2. Creates file in /Pending_Approval/
3. Human reviews and moves to /Approved/ or /Rejected/
4. Orchestrator detects movement
5. Action is executed or cancelled
```

---

### 5. **plan-creator** (NEW)
**Purpose:** Create structured Plan.md files for multi-step tasks

**Tools:**
- `create_plan` - Create a new plan with checkboxes
- `update_plan` - Update plan progress
- `get_plan_status` - Get plan completion status

**Files to Create:**
```
.qwen/skills/plan-creator/
├── SKILL.md
└── scripts/
    └── plan-manager.py
```

**Plan.md Format:**
```markdown
---
type: plan
objective: Process invoice request
created: 2026-02-26T20:00:00Z
status: in_progress
---

# Plan: Process Invoice Request

## Steps
- [x] Read action file
- [x] Identify client details
- [ ] Generate invoice PDF
- [ ] Send via email
- [ ] Log transaction

## Notes
Waiting for approval before sending...
```

---

### 6. **scheduler** (NEW)
**Purpose:** Schedule recurring tasks (cron/Task Scheduler)

**Files to Create:**
```
scripts/
├── scheduler.py           # Main scheduler script
├── tasks/
│   ├── daily_briefing.py  # Daily briefing task
│   └── weekly_audit.py    # Weekly business audit
└── requirements.txt
```

**Scheduled Tasks:**
| Task | Frequency | Time |
|------|-----------|------|
| Daily Briefing | Daily | 8:00 AM |
| Process Pending | Every 30 min | All day |
| Weekly Audit | Sunday | 10:00 PM |

**Windows Task Scheduler Setup:**
```powershell
# Create scheduled task
schtasks /create /tn "AI_Employee_Daily" /tr "python scheduler.py" /sc daily /st 08:00
```

---

## Existing Skills (Bronze Tier)

### browsing-with-playwright (EXISTING - Already Complete)
**Status:** ✅ Already implemented

**Tools Available:**
- `browser_navigate` - Navigate to URL
- `browser_click` - Click element
- `browser_type` - Type text
- `browser_fill_form` - Fill forms
- `browser_snapshot` - Get page snapshot
- `browser_take_screenshot` - Take screenshot
- `browser_close` - Close browser

**Used For:**
- LinkedIn posting (via LinkedIn Web)
- WhatsApp monitoring (via WhatsApp Web)
- General web automation

---

## Skills Dependency Graph

```
Silver Tier
├── Bronze Tier (Complete)
│   ├── FileSystem Watcher ✓
│   ├── Orchestrator ✓
│   └── Dashboard ✓
│
├── New Watchers
│   ├── Gmail Watcher → email-mcp
│   └── WhatsApp Watcher → browsing-with-playwright
│
├── MCP Servers
│   ├── Email MCP (NEW)
│   ├── LinkedIn MCP (NEW)
│   └── Playwright MCP (EXISTING ✓)
│
├── Workflow Skills
│   ├── Approval Workflow (NEW)
│   └── Plan Creator (NEW)
│
└── Scheduling
    └── Scheduler (NEW)
```

---

## Implementation Order (Recommended)

1. **email-mcp** - Foundation for email actions
2. **approval-workflow** - Required for safe operations
3. **plan-creator** - Enables multi-step tasks
4. **gmail-watcher** - Second watcher (Silver requirement)
5. **scheduler** - Automation trigger
6. **linkedin-posting** - Business feature

---

## File Structure After Silver Tier

```
Personal-AI-Employee/
├── .qwen/skills/
│   ├── browsing-with-playwright/  ✓ Bronze
│   ├── email-mcp/                 ⏳ Silver
│   ├── linkedin-posting/          ⏳ Silver
│   ├── approval-workflow/         ⏳ Silver
│   └── plan-creator/              ⏳ Silver
│
├── watchers/
│   ├── base_watcher.py            ✓ Bronze
│   ├── filesystem_watcher.py      ✓ Bronze
│   ├── gmail_watcher.py           ⏳ Silver
│   └── whatsapp_watcher.py        ⏳ Silver
│
├── scripts/
│   ├── scheduler.py               ⏳ Silver
│   └── tasks/
│       ├── daily_briefing.py      ⏳ Silver
│       └── weekly_audit.py        ⏳ Silver
│
├── orchestrator.py                ✓ Bronze (enhanced)
├── update_dashboard.py            ✓ Bronze
└── AI_Employee_Vault/
    ├── Dashboard.md               ✓ Bronze
    ├── Company_Handbook.md        ✓ Bronze
    ├── Business_Goals.md          ✓ Bronze
    ├── Plans/                     ⏳ Silver (populated)
    ├── Pending_Approval/          ⏳ Silver (workflow)
    └── Logs/                      ✓ Bronze (enhanced)
```

---

## Testing Strategy

### Unit Tests
- Each skill has `test_<skill>.py`
- Mock external APIs

### Integration Tests
- `test_silver_tier.py` - Full workflow test
- Test approval flow end-to-end
- Test scheduled task execution

### Demo Scenarios
1. **Email Processing Flow**
   - Gmail watcher detects email
   - Creates action file
   - Qwen creates plan
   - Requests approval
   - Human approves
   - Email sent via MCP

2. **LinkedIn Posting Flow**
   - Qwen drafts post
   - Creates approval request
   - Human approves
   - Post published via MCP

3. **Daily Briefing Flow**
   - Scheduler triggers at 8 AM
   - Qwen generates briefing
   - Updates Dashboard
   - Notifies user

---

## Success Criteria (Silver Tier)

- [ ] 2+ watchers running (FileSystem + Gmail)
- [ ] Email MCP server working
- [ ] Approval workflow functional
- [ ] Plans created automatically
- [ ] Scheduler running
- [ ] LinkedIn posting works (or via Playwright)
- [ ] All functionality wrapped as Qwen Skills

---

*Silver Tier Skills Plan - AI Employee v0.2*
