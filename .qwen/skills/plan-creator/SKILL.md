---
name: plan-creator
description: |
  Create and manage structured plans for multi-step tasks.
  Generate Plan.md files with checkboxes, track progress, and manage task completion.
  Use when tasks require multiple steps or complex reasoning.
---

# Plan Creator

Create and manage structured plans for Qwen Code to execute.

## Quick Reference

### Create Plan

```bash
python .qwen/skills/plan-creator/scripts/plan-manager.py create \
  --objective "Process invoice request" \
  --steps "Read action file,Identify client,Generate invoice,Send email,Log transaction"
```

### Update Plan

```bash
python .qwen/skills/plan-creator/scripts/plan-manager.py update \
  --file "PLAN_invoice_2026-02-26.md" \
  --step 3 \
  --status "completed"
```

### Get Plan Status

```bash
python .qwen/skills/plan-creator/scripts/plan-manager.py status \
  --file "PLAN_invoice_2026-02-26.md"
```

### List Active Plans

```bash
python .qwen/skills/plan-creator/scripts/plan-manager.py list
```

---

## Plan.md Format

```markdown
---
type: plan
objective: Process invoice request
created: 2026-02-26T10:30:00Z
status: in_progress
priority: high
---

# Plan: Process Invoice Request

## Context
- **Source:** FILE_DROP_invoice_txt_20260226_103000.md
- **Client:** Acme Corp
- **Amount:** $2,500

## Steps
- [x] Read action file and extract details
- [x] Identify client information
- [ ] Generate invoice PDF
- [ ] Send via email (requires approval)
- [ ] Log transaction to Dashboard

## Notes
Waiting for approval before sending email.

## Timeline
- Started: 2026-02-26T10:30:00Z
- Target: 2026-02-26T12:00:00Z
```

---

## Script Usage

### Create Plan

```bash
python plan-manager.py create \
  --objective "<objective>" \
  --steps "<step1>,<step2>,<step3>" \
  --priority "<high|normal|low>" \
  --context "<json_context>"
```

**Parameters:**
- `--objective`: What the plan aims to achieve
- `--steps`: Comma-separated list of steps
- `--priority`: Priority level (default: normal)
- `--context`: JSON string with additional context

**Example:**
```bash
python plan-manager.py create \
  --objective "Reply to client email" \
  --steps "Read email,Draft response,Check handbook,Send response" \
  --priority "high" \
  --context '{"from": "client@example.com", "subject": "Urgent"}'
```

### Update Plan Step

```bash
python plan-manager.py update \
  --file "<filename.md>" \
  --step <step_number> \
  --status "<completed|failed|skipped>" \
  --note "<optional_note>"
```

### Get Status

```bash
python plan-manager.py status --file "<filename.md>"
```

**Output:**
```
Plan: Process invoice request
Status: in_progress
Progress: 2/5 steps completed (40%)

Steps:
  [x] 1. Read action file and extract details
  [x] 2. Identify client information
  [ ] 3. Generate invoice PDF
  [ ] 4. Send via email (requires approval)
  [ ] 5. Log transaction to Dashboard
```

---

## Integration with Qwen Code

Qwen Code automatically:
1. Creates plan when processing complex tasks
2. Updates step status as it works
3. Adds notes for human visibility
4. Moves plan to Done when complete

---

## Plan Lifecycle

```
1. Task detected in Needs_Action/
         ↓
2. Qwen creates Plan.md in Plans/
         ↓
3. Qwen executes steps, updating status
         ↓
4. Plan moved to Done/ when complete
```

---

## Examples

### Simple Plan (2-3 steps)

```bash
python plan-manager.py create \
  --objective "Archive old files" \
  --steps "Find files older than 30 days,Move to Archive/,Update log"
```

### Complex Plan (with context)

```bash
python plan-manager.py create \
  --objective "Process client invoice" \
  --steps "Read request,Verify client details,Calculate amount,Generate PDF,Request approval,Send email,Log transaction" \
  --priority "high" \
  --context '{"client": "Acme Corp", "amount": 2500, "service": "Web Design"}'
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plan not created | Check Plans/ folder exists |
| Step update fails | Verify step number is valid |
| Status shows wrong | Re-run status command |
| Plan stuck | Check for pending approvals |

---

*Plan Creator Skill v0.1 - Silver Tier*
