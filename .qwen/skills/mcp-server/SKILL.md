---
name: mcp-server
description: |
  Unified MCP (Model Context Protocol) server manager.
  Start, stop, and manage multiple MCP servers for email, browser, LinkedIn, etc.
  Provides a single interface for all external integrations.
---

# MCP Server Manager

Manage all MCP servers from one place.

## Quick Start

### Start All Servers

```bash
python .qwen/skills/mcp-server/scripts/mcp-manager.py start-all
```

### Start Specific Server

```bash
python mcp-manager.py start email
python mcp-manager.py start browser
python mcp-manager.py start linkedin
```

### Check Status

```bash
python mcp-manager.py status
```

### Stop All Servers

```bash
python mcp-manager.py stop-all
```

---

## Available MCP Servers

| Server | Port | Purpose |
|--------|------|---------|
| browser | 8808 | Playwright browser automation |
| email | 8809 | SMTP/Gmail email sending |
| linkedin | 8810 | LinkedIn API |
| approval | 8811 | Approval workflow |

---

## Server Configuration

### config.json

```json
{
  "servers": {
    "browser": {
      "enabled": true,
      "port": 8808,
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--port", "8808"]
    },
    "email": {
      "enabled": true,
      "port": 8809,
      "command": "python",
      "args": [".qwen/skills/email-mcp/scripts/email-server.py", "--serve"]
    },
    "linkedin": {
      "enabled": true,
      "port": 8810,
      "command": "python",
      "args": [".qwen/skills/linkedin-posting/scripts/linkedin-mcp.py", "--serve"]
    }
  }
}
```

---

## Script Usage

### Start Server

```bash
python mcp-manager.py start <server_name>
```

### Stop Server

```bash
python mcp-manager.py stop <server_name>
```

### Restart Server

```bash
python mcp-manager.py restart <server_name>
```

### Health Check

```bash
python mcp-manager.py health <server_name>
```

### List Available Tools

```bash
python mcp-manager.py tools <server_name>
```

---

## Auto-Start on Boot

### Windows (Task Scheduler)

```powershell
# Create task to start MCP servers on boot
schtasks /create /tn "MCP_Servers" /tr "python mcp-manager.py start-all" /sc onstart /ru SYSTEM
```

### Linux (systemd)

```ini
# /etc/systemd/system/mcp-servers.service
[Unit]
Description=MCP Servers
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /path/to/mcp-manager.py start-all
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable mcp-servers
sudo systemctl start mcp-servers
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in config.json |
| Server won't start | Check logs in Logs/mcp/ |
| Connection refused | Verify server is running: `mcp-manager.py status` |
| Tool not found | Run `mcp-manager.py tools <server>` |

---

*MCP Server Manager v0.1 - Silver Tier*
