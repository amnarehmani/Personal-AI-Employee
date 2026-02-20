# Claude Code Interaction Example

This file demonstrates how Claude Code can read from and write to the Obsidian vault.

## Process Example

When Claude Code detects files in the `/Needs_Action` folder, it can:

1. Read the content of the files
2. Analyze the content according to the Company Handbook
3. Create appropriate response files in the `/Plans` folder
4. Move completed items to the `/Done` folder

## Current Status

- Files in `/Inbox`: `{{inbox_count}}`
- Files in `/Needs_Action`: `{{needs_action_count}}`
- Files in `/Done`: `{{done_count}}`

## Example Processing

If a file is found in `/Needs_Action`, Claude Code will:

1. Read the file content
2. Determine appropriate action based on Company Handbook rules
3. Either handle automatically or create approval request in `/Pending_Approval`
4. Update Dashboard.md with status
5. Move processed files to `/Done`

---
*This demonstrates the read/write capability of Claude Code to the vault*