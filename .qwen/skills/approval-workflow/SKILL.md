---
name: approval-workflow
description: |
  Human-in-the-loop approval system for sensitive actions.
  Create approval requests, check status, and manage pending approvals.
  Use when actions require human approval before execution (payments, emails to new contacts, etc.).
---

# Approval Workflow

Manage human-in-the-loop approvals for sensitive actions.

## Quick Reference

### Create Approval Request

```bash
python .qwen/skills/approval-workflow/scripts/approval-manager.py create \
  --type "payment" \
  --action "send_payment" \
  --amount "500.00" \
  --recipient "Client A" \
  --reason "Invoice #1234 payment"
```

### Check Approval Status

```bash
python .qwen/skills/approval-workflow/scripts/approval-manager.py check \
  --file "PAYMENT_Client_A_2026-02-26.md"
```

### List Pending Approvals

```bash
python .qwen/skills/approval-workflow/scripts/approval-manager.py list
```

---

## Approval File Format

```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Client A
reason: Invoice #1234 payment
created: 2026-02-26T10:30:00Z
expires: 2026-02-27T10:30:00Z
status: pending
---

# Approval Request: Payment

## Details
- **Action:** Send Payment
- **Amount:** $500.00
- **Recipient:** Client A (Bank: XXXX1234)
- **Reference:** Invoice #1234

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder.

## Expiry
This request expires on: 2026-02-27T10:30:00Z
```

---

## Approval Thresholds (from Company_Handbook)

| Action Category | Auto-Approve | Require Approval |
|-----------------|--------------|------------------|
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, ≥ $50 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

---

## Workflow

```
1. Qwen detects action requiring approval
         ↓
2. Create approval request file in /Pending_Approval/
         ↓
3. Human reviews file
         ↓
4a. Move to /Approved/ → Action executed
         ↓
4b. Move to /Rejected/ → Action cancelled
```

---

## Script Usage

### Create Approval Request

```bash
python approval-manager.py create \
  --type "<action_type>" \
  --action "<action_name>" \
  --details "<json_details>"
```

**Parameters:**
- `--type`: Type of action (payment, email, social_post, etc.)
- `--action`: Specific action to perform
- `--details`: JSON string with action details
- `--expires-hours`: Hours until expiry (default: 24)

**Example:**
```bash
python approval-manager.py create \
  --type "email" \
  --action "send_email" \
  --details '{"to": "newclient@example.com", "subject": "Proposal", "body": "..."}'
```

### Check Status

```bash
python approval-manager.py check --file "<filename.md>"
```

**Returns:**
- `pending` - Awaiting approval
- `approved` - Approved, ready for execution
- `rejected` - Rejected, do not execute
- `expired` - Expired, no longer valid

### List Pending

```bash
python approval-manager.py list
```

**Output:**
```
Pending Approvals:
  1. PAYMENT_Client_A_2026-02-26.md - $500.00 - Created 2 hours ago
  2. EMAIL_new_client_2026-02-26.md - Email to newclient@example.com - Created 30 min ago
```

### Process Approved

```bash
python approval-manager.py process
```

Moves all files from `/Approved/` to `/Done/` after execution.

---

## Integration with Orchestrator

The orchestrator automatically:
1. Detects new files in `/Pending_Approval/`
2. Notifies user (via dashboard update)
3. Monitors `/Approved/` for files to execute
4. Executes approved actions
5. Moves completed to `/Done/`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Approval not detected | Check file is in correct folder |
| Status shows wrong | Run `approval-manager.py check` |
| Expired request | Create new approval request |
| File moved but not executed | Check orchestrator logs |

---

*Approval Workflow Skill v0.1 - Silver Tier*
