"""
Orchestrator for AI Employee

This script coordinates the various components of the AI Employee system:
- Monitors the Needs_Action folder
- Processes files using Claude Code (simulated)
- Updates Dashboard accordingly
"""

import time
import logging
import json
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AI_Employee_Orchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.logs = self.vault_path / 'Logs'

        # Ensure all directories exist
        for directory in [self.inbox, self.needs_action, self.done,
                         self.plans, self.pending_approval, self.logs]:
            directory.mkdir(exist_ok=True)

        logger.info(f"Initialized orchestrator with vault: {vault_path}")

    def process_needs_action(self):
        """Process files in the Needs_Action folder"""
        needs_action_files = list(self.needs_action.glob("*.md"))

        if not needs_action_files:
            logger.info("No files in Needs_Action folder")
            return

        logger.info(f"Found {len(needs_action_files)} files in Needs_Action")

        for file_path in needs_action_files:
            logger.info(f"Processing: {file_path.name}")

            # Read the file content
            try:
                content = file_path.read_text(encoding='utf-8')

                # Simulate Claude Code processing
                processed_content = self.simulate_claude_processing(content, file_path.name)

                # Determine what to do based on content
                if "approval" in content.lower() or "urgent" in content.lower():
                    # Create approval request
                    self.create_approval_request(file_path, content)
                else:
                    # Process directly and move to Done
                    self.process_directly(file_path, processed_content)

                # Update dashboard
                self.update_dashboard()

            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")

    def simulate_claude_processing(self, content: str, filename: str):
        """Simulate what Claude Code would do with the content"""
        logger.info(f"Simulating Claude Code processing for: {filename}")

        # In real implementation, this would call Claude Code API
        # For now, just return a processed version
        return f"""
# Processed by AI Employee
- Original file: {filename}
- Processed at: {datetime.now().isoformat()}
- Content analyzed and appropriate action taken

## Original Content:
{content}
"""

    def create_approval_request(self, original_file, content):
        """Create an approval request for human review"""
        approval_file = self.pending_approval / f"APPROVAL_{original_file.name}"

        approval_content = f"""---
action: approval_required
original_file: {original_file.name}
created: {datetime.now().isoformat()}
status: pending
---

# Approval Required

The AI Employee requires human approval to process this item:

## Original Content
{content}

## Recommended Action
[To be filled by AI]

## To Approve
Move this file to the /Approved folder (to be created)

## To Reject
Move this file to the /Rejected folder (to be created)

---
*Created by AI Employee at {datetime.now().isoformat()}*
"""

        approval_file.write_text(approval_content)
        logger.info(f"Created approval request: {approval_file.name}")

        # Move original to Done with note
        done_file = self.done / f"REQ_APPROVAL_{original_file.name}"
        original_file.rename(done_file)
        logger.info(f"Moved original to Done: {done_file.name}")

    def process_directly(self, original_file, processed_content):
        """Process file directly without approval"""
        # Create a plan file if needed
        plan_file = self.plans / f"PLAN_{original_file.stem}.md"
        plan_content = f"""---
created: {datetime.now().isoformat()}
status: processed
original: {original_file.name}
---

# Processing Plan

## Completed Actions
- File processed automatically by AI Employee
- Appropriate action taken per Company Handbook
- Status updated in dashboard

## Summary
{processed_content}
"""

        plan_file.write_text(plan_content)

        # Move original to Done
        done_file = self.done / f"PROCESSED_{original_file.name}"
        original_file.rename(done_file)

        logger.info(f"Processed file directly: {done_file.name}")

    def update_dashboard(self):
        """Update the dashboard with current status"""
        dashboard_path = self.vault_path / 'Dashboard.md'

        if dashboard_path.exists():
            content = dashboard_path.read_text()
        else:
            content = "# AI Employee Dashboard\n\n## Executive Summary\n"

        # Count files in each folder
        inbox_count = len(list(self.inbox.glob("*")))
        needs_action_count = len(list(self.needs_action.glob("*")))
        done_count = len(list(self.done.glob("*")))
        pending_approval_count = len(list(self.pending_approval.glob("*")))

        # Update the dashboard
        updated_content = content.replace(
            "## Recent Activity",
            f"""## System Status
- Files in Queue: {needs_action_count}
- Active Tasks: {needs_action_count + pending_approval_count}
- Files in Inbox: {inbox_count}
- Files Completed: {done_count}
- Pending Approval: {pending_approval_count}

## Recent Activity"""
        )

        # Add recent activity entry
        activity_entry = f"- {datetime.now().strftime('%Y-%m-%d %H:%M')}: System checked for new tasks\n"

        if "## Recent Activity" in updated_content:
            updated_content = updated_content.replace(
                "## Recent Activity",
                f"## Recent Activity\n- {datetime.now().strftime('%Y-%m-%d %H:%M')}: System checked for new tasks"
            )
        else:
            updated_content += f"\n## Recent Activity\n- {datetime.now().strftime('%Y-%m-%d %H:%M')}: System checked for new tasks\n"

        dashboard_path.write_text(updated_content)
        logger.info("Dashboard updated")

    def log_activity(self, activity: str):
        """Log activity to the logs folder"""
        log_file = self.logs / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "source": "orchestrator"
        }

        # Read existing logs or create new list
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                logs = []
        else:
            logs = []

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    def run_once(self):
        """Run one cycle of processing"""
        logger.info("Starting processing cycle")
        self.process_needs_action()
        logger.info("Processing cycle completed")

    def run_continuously(self, interval=30):
        """Run continuously with specified interval between checks"""
        logger.info(f"Starting continuous run, checking every {interval} seconds")

        while True:
            try:
                self.run_once()
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Stopping orchestrator (KeyboardInterrupt)")
                break
            except Exception as e:
                logger.error(f"Error in orchestrator cycle: {e}")
                time.sleep(10)  # Wait before trying again

def main():
    """Main function to run the orchestrator"""
    vault_path = Path.cwd()  # Current working directory

    orchestrator = AI_Employee_Orchestrator(str(vault_path))

    print("AI Employee Orchestrator")
    print("=" * 30)
    print("1. Process once and exit")
    print("2. Run continuously")
    print("3. Just update dashboard")

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice == "1":
        orchestrator.run_once()
    elif choice == "2":
        interval = input("Check interval in seconds (default 30): ").strip()
        interval = int(interval) if interval.isdigit() else 30
        orchestrator.run_continuously(interval)
    elif choice == "3":
        orchestrator.update_dashboard()
        print("Dashboard updated")
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()