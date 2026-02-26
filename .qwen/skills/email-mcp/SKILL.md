---
name: email-mcp
description: |
  Email sending via SMTP/Gmail. Send emails, create drafts, and search inbox.
  Use when tasks require sending emails to clients, contacts, or stakeholders.
  Requires email credentials configured.
---

# Email MCP

Send emails via SMTP or Gmail API.

## Server Lifecycle

### Start Server
```bash
bash .qwen/skills/email-mcp/scripts/start-server.sh
```

### Stop Server
```bash
bash .qwen/skills/email-mcp/scripts/stop-server.sh
```

## Quick Reference

### Send Email

```bash
python .qwen/skills/email-mcp/scripts/email-server.py send \
  --to "client@example.com" \
  --subject "Invoice #1234" \
  --body "Please find attached your invoice..." \
  --attachments "/path/to/file.pdf"
```

### Create Draft

```bash
python .qwen/skills/email-mcp/scripts/email-server.py draft \
  --to "client@example.com" \
  --subject "Proposal" \
  --body "Dear Client,..."
```

### Search Emails

```bash
python .qwen/skills/email-mcp/scripts/email-server.py search \
  --query "from:client@example.com" \
  --limit 10
```

---

## Configuration

Create `.env` file in project root:

```bash
# Email Configuration
EMAIL_PROVIDER=gmail  # or smtp
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_client_secret
GMAIL_REFRESH_TOKEN=your_refresh_token

# OR for SMTP
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## Approval Requirements

Per Company_Handbook.md:

| Email Type | Approval Required |
|------------|-------------------|
| Reply to known contact | No (auto-approve) |
| Reply to new contact | Yes |
| Bulk email (>10 recipients) | Yes |
| Email with attachment | Yes |

---

## Script Usage

### Send Email

```bash
python email-server.py send \
  --to "<email>" \
  --subject "<subject>" \
  --body "<body>" \
  [--attachments "<file1,file2>"] \
  [--cc "<email>"] \
  [--bcc "<email>"]
```

### Search

```bash
python email-server.py search --query "<Gmail query>" --limit <n>
```

**Gmail Query Examples:**
- `is:unread` - Unread emails
- `is:important` - Important emails
- `from:client@example.com` - From specific sender
- `subject:invoice` - With "invoice" in subject
- `newer_than:1d` - From last day

---

## Integration with Approval Workflow

For emails requiring approval:

1. Create draft using `email-server.py draft`
2. Create approval request using `approval-manager.py create`
3. Human approves by moving file to /Approved
4. Send draft using `email-server.py send-draft`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Authentication failed | Check credentials in .env |
| Email not sent | Check SMTP settings |
| Attachment not found | Verify file path is absolute |

---

*Email MCP Skill v0.1 - Silver Tier*
