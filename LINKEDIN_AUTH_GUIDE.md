# LinkedIn Authentication - Manual Method

## The Problem
Automated LinkedIn login is unreliable. Manual login is the recommended approach for Silver Tier.

---

## Step-by-Step: Manual LinkedIn Login

### Step 1: Start Playwright Server

Open a terminal and run:

```bash
cd "C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee"
npx @playwright/mcp@latest --port 8808 --shared-browser-context
```

**Keep this terminal open!**

A browser window will open automatically.

### Step 2: Navigate to LinkedIn

In the browser window:
1. Type in address bar: `https://www.linkedin.com`
2. Press Enter
3. Login with your LinkedIn credentials
4. **Keep the browser window open**

### Step 3: Verify Connection (New Terminal)

Open another terminal and run:

```bash
cd "C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee"
python .qwen/skills/browsing-with-playwright/scripts/verify.py
```

Expected: `[PASS] Playwright MCP server process found`

### Step 4: Create Post Draft

```bash
python watchers/linkedin_watcher.py --post --content "Testing LinkedIn from AI Employee!"
```

Check the draft:
```
AI_Employee_Vault/Pending_Approval/LINKEDIN_Testing_LinkedIn_*.md
```

---

## How It Works

```
1. Playwright starts → Opens visible browser
       ↓
2. You manually login to LinkedIn
       ↓
3. Browser session is shared (--shared-browser-context)
       ↓
4. LinkedIn Watcher can now use the logged-in session
       ↓
5. Create drafts → Approve → Auto-publish
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `npx @playwright/mcp@latest --port 8808` | Start server (visible browser) |
| `python watchers/linkedin_watcher.py --post --content "..."` | Create post draft |
| `python .qwen/skills/browsing-with-playwright/scripts/verify.py` | Verify server |

---

## Troubleshooting

### Browser doesn't open
- By default, browser IS visible (not headless)
- Check terminal for errors
- Try: `npx @playwright/mcp@latest --port 8808`

### "Connection refused" error
- Server may not be running
- Run verify script first
- Restart Playwright server

### LinkedIn login fails
- Clear browser cookies
- Try incognito mode
- Check your LinkedIn credentials

---

## Stop Server

When done:
```bash
# Press Ctrl+C in the Playwright terminal
# Or close the browser window
```

---

*LinkedIn Manual Authentication - Silver Tier*
