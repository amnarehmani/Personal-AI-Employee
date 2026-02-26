---
name: linkedin-posting
description: |
  Post updates to LinkedIn automatically. Create posts, schedule content,
  and track engagement. Uses LinkedIn API or browser automation via Playwright.
  Requires human approval before posting.
---

# LinkedIn Posting

Automate LinkedIn posts for business development.

## Quick Start

### Option 1: LinkedIn API (Recommended for Production)

```bash
# 1. Create LinkedIn App at: https://www.linkedin.com/developers/apps

# 2. Get credentials
# - Client ID
# - Client Secret
# - Access Token

# 3. Configure .env file
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_ORGANIZATION_ID=your_org_id

# 4. Post
python .qwen/skills/linkedin-posting/scripts/linkedin-mcp.py post \
  --text "Excited to announce our new service!"
```

### Option 2: Playwright Browser Automation

```bash
# Uses existing browsing-with-playwright skill
# Navigate to LinkedIn and post via browser

python .qwen/skills/linkedin-posting/scripts/linkedin-browser.py post \
  --text "Your post content here"
```

---

## Configuration

### LinkedIn API Setup

1. Go to [LinkedIn Developers](https://www.linkedin.com/developers/apps)
2. Create new app
3. Get credentials:
   - Client ID
   - Client Secret
   - Generate Access Token
4. Note Organization ID (for company page posts)

### Environment Variables

```bash
# .env file
LINKEDIN_CLIENT_ID=xxx
LINKEDIN_CLIENT_SECRET=xxx
LINKEDIN_ACCESS_TOKEN=xxx
LINKEDIN_ORGANIZATION_ID=xxx
```

---

## Approval Workflow

All LinkedIn posts require approval before publishing:

```
1. Qwen drafts post
         ↓
2. Creates file in /Pending_Approval/
         ↓
3. Human reviews content
         ↓
4a. Move to /Approved/ → Post published
         ↓
4b. Move to /Rejected/ → Post discarded
```

---

## Script Usage

### Create Post (API)

```bash
python linkedin-mcp.py post \
  --text "Your post content" \
  --visibility "PUBLIC" \
  --schedule "2026-02-27T09:00:00Z"
```

### Create Post (Browser)

```bash
python linkedin-browser.py post \
  --text "Your post content" \
  --image "/path/to/image.png"
```

### Create Draft

```bash
python linkedin-mcp.py draft \
  --text "Draft content" \
  --title "Post title"
```

### Get Analytics

```bash
python linkedin-mcp.py analytics \
  --post-id "urn:li:share:123456789"
```

---

## Post File Format

```markdown
---
type: linkedin_post
content: "Excited to announce..."
visibility: PUBLIC
created: 2026-02-26T10:00:00Z
status: pending_approval
---

# LinkedIn Post Draft

## Content

Excited to announce our new service!

## Hashtags
#Business #Innovation #Tech

## Scheduled For
2026-02-27 09:00 AM

---
*To approve: Move to /Approved folder*
```

---

## Best Practices

### Content Guidelines
- Keep posts under 1,300 characters
- Include 3-5 relevant hashtags
- Add images for higher engagement
- Post during business hours (9 AM - 5 PM)

### Approval Rules
- Marketing posts: Auto-approve if pre-scheduled
- Product announcements: Require approval
- Response to comments: Require approval
- Sensitive topics: Always require approval

---

## Integration with Orchestrator

The orchestrator:
1. Detects approved posts in /Approved/
2. Publishes to LinkedIn
3. Logs post ID and analytics
4. Moves completed to /Done/

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API auth failed | Refresh access token |
| Post not published | Check approval status |
| Image upload failed | Verify file path |
| Rate limited | Wait 24 hours |

---

*LinkedIn Posting Skill v0.1 - Silver Tier*
