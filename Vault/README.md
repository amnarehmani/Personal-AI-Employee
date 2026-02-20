# Personal AI Employee - Bronze Tier Implementation

This project implements the Bronze Tier requirements of the Personal AI Employee Hackathon, creating a foundation for an autonomous AI employee system.

## Features Implemented

### 1. Obsidian Vault Structure
- **Dashboard.md**: Central dashboard showing system status and activity
- **Company_Handbook.md**: Rules and guidelines for the AI employee
- **Business_Goals.md**: Business objectives and metrics
- **Folder Structure**:
  - `/Inbox`: Incoming files and tasks
  - `/Needs_Action`: Tasks requiring processing
  - `/Done`: Completed tasks
  - `/Plans`: Processing plans
  - `/Pending_Approval`: Items requiring human approval
  - `/Logs`: System logs

### 2. File System Watcher
- `filesystem_watcher.py`: Monitors the Inbox folder for new files
- Automatically moves files from Inbox to Needs_Action when detected
- Creates metadata files with processing instructions

### 3. Claude Code Integration
- Demonstrates Claude Code's ability to read from and write to the vault
- `Claude_Code_Interaction.md`: Example of how Claude interacts with the system

### 4. Orchestrator
- `orchestrator.py`: Coordinates system components
- Processes files in Needs_Action folder
- Updates Dashboard with system status
- Creates approval requests for sensitive actions

### 5. Dependencies
- `requirements.txt`: Lists required Python packages

## Setup Instructions

1. Install required packages:
   ```
   pip install -r requirements.txt
   ```

2. Start the file system watcher:
   ```
   python filesystem_watcher.py
   ```

3. Run the orchestrator to process tasks:
   ```
   python orchestrator.py
   ```

## How It Works

1. **File Detection**: The file system watcher monitors the Inbox folder
2. **File Movement**: New files are automatically moved to Needs_Action
3. **Processing**: The orchestrator processes files in Needs_Action
4. **Decision Making**: Based on content, the system either processes directly or creates approval requests
5. **Status Updates**: Dashboard is updated with current system status
6. **Logging**: All activities are logged for audit purposes

## Bronze Tier Completion

- [x] Obsidian vault with Dashboard.md and Company_Handbook.md
- [x] One working Watcher script (File System Watcher)
- [x] Claude Code successfully reading from and writing to the vault
- [x] Basic folder structure: /Inbox, /Needs_Action, /Done
- [x] All AI functionality implemented as documented processes

## Next Steps (Silver/Gold Tiers)

Future enhancements could include:
- Gmail watcher implementation
- WhatsApp watcher implementation
- MCP server integration
- More sophisticated approval workflows
- Automated social media posting
- Accounting system integration

---
*Built for the Personal AI Employee Hackathon - Bronze Tier Complete*