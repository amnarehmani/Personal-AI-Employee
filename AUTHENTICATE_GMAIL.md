# Gmail Watcher - First Time Authentication

## IMPORTANT: Run These Steps

### Step 1: Open Terminal in Project Root

**DO NOT** run from inside `AI_Employee_Vault` folder.

Go to the project root:
```
C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee
```

### Step 2: Run Authentication Command

```bash
cd "C:\Users\Amna Rehman\OneDrive\Documents\GitHub\Personal-AI-Employee"
python watchers/gmail_watcher.py --auth
```

### Step 3: Authorize in Browser

A browser window should open automatically. If it does:

1. **Sign in** to your Google account (the one you want to monitor)
2. **Click "Allow"** when asked for permissions
3. The page will show "Authentication successful" or similar
4. The terminal will show "[Auth] Authentication successful!"

### Step 4: Verify Token Created

After successful auth, check that `token.json` was created:
```bash
dir token.json
```

You should see:
```
token.json    Created: 2026-02-26
```

### Step 5: Test Connection

```bash
python watchers/gmail_watcher.py --test
```

Expected output:
```
[Test] Connected to: your-email@gmail.com
[Test] Unread emails: X+
[Test] Connection test PASSED
```

---

## If Browser Doesn't Open Automatically

The script is waiting for browser authentication. Try these:

### Option A: Manual Browser Auth

1. Copy the authorization URL from terminal (if shown)
2. Paste in your browser
3. Complete authentication
4. Browser will redirect to localhost (this is normal)

### Option B: Use Localhost URL

Sometimes the browser opens but doesn't redirect back. Look for a URL like:
```
http://localhost:8080/?code=...
```

Copy this URL and paste it in the terminal if prompted.

---

## Troubleshooting

### "Port already in use"
```bash
# Kill any process on port 8080
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### "Credentials invalid"
- Check `credentials.json` exists in project root
- Verify it has the correct format

### "Token expired"
```bash
# Delete old token
del token.json

# Re-authenticate
python watchers/gmail_watcher.py --auth
```

---

## After Authentication

Once authenticated successfully:

### Test the watcher:
```bash
python watchers/gmail_watcher.py --test
```

### Run continuously:
```bash
python watchers/gmail_watcher.py
```

### Run once (for scheduler):
```bash
python watchers/gmail_watcher.py --once
```

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python watchers/gmail_watcher.py --auth` | First-time authentication |
| `python watchers/gmail_watcher.py --test` | Test connection |
| `python watchers/gmail_watcher.py` | Run continuously |
| `python watchers/gmail_watcher.py --once` | Run once (scheduler) |
| `python watchers/gmail_watcher.py --status` | Show status |

---

*Gmail Watcher v0.1 - Silver Tier*
