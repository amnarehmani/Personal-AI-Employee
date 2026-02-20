# Agent Skills for Personal AI Employee

This file describes the agent skills that would be implemented in a full Claude Code Agent setup, per the hackathon requirements.

## Skill 1: Process Needs Action Files
**Purpose:** Process files in the Needs_Action folder
**Trigger:** When files exist in /Needs_Action directory
**Actions:**
- Read file content
- Apply Company Handbook rules
- Either process automatically or create approval request
- Create plan in /Plans if needed
- Move to /Done when complete

## Skill 2: Update Dashboard
**Purpose:** Keep the dashboard current with system status
**Trigger:** When any task is processed
**Actions:**
- Count files in each directory
- Update status metrics
- Add recent activity entry
- Save to Dashboard.md

## Skill 3: File Monitoring
**Purpose:** Monitor the Inbox for new files
**Trigger:** File system watcher detects new file
**Actions:**
- Move file from /Inbox to /Needs_Action
- Create metadata file with processing instructions
- Log the activity

## Skill 4: Approval Workflow
**Purpose:** Handle approval-required tasks
**Trigger:** When content requires human approval
**Actions:**
- Create approval request in /Pending_Approval
- Note in original task that approval is needed
- Update dashboard with pending approval count

## Skill 5: System Reporting
**Purpose:** Generate regular system reports
**Trigger:** Scheduled time or on-demand
**Actions:**
- Analyze completed tasks
- Calculate metrics
- Create business summary
- Update appropriate report files

---
*Agent Skills defined for Bronze Tier implementation*