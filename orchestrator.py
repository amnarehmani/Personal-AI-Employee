#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Orchestrator for AI Employee - Qwen Code Edition

This script orchestrates the AI Employee workflow:
1. Monitors Needs_Action folder for new tasks
2. Automatically triggers Qwen Code to process tasks
3. Manages task completion flow
4. Logs all activities

Usage:
    python orchestrator.py AI_Employee_Vault

For Bronze Tier: Orchestrator detects new action files and 
automatically invokes Qwen Code for processing.
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from datetime import datetime


class Orchestrator:
    """Orchestrates the AI Employee workflow with Qwen Code."""
    
    def __init__(self, vault_path: str, check_interval: int = 30):
        """
        Initialize the orchestrator.
        
        Args:
            vault_path: Path to the Obsidian vault root
            check_interval: Seconds between checks (default: 30)
        """
        self.vault_path = Path(vault_path).resolve()
        self.check_interval = check_interval
        self.needs_action = self.vault_path / 'Needs_Action'
        self.done = self.vault_path / 'Done'
        self.logs = self.vault_path / 'Logs'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        
        # Ensure directories exist
        for directory in [self.needs_action, self.done, self.logs, self.plans, self.pending_approval]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Track processed files
        self.processed_files = set()
        
        # Qwen Code command
        self.qwen_command = self._find_qwen_command()
        
        print(f"[Orchestrator] Vault path: {self.vault_path}")
        print(f"[Orchestrator] Check interval: {self.check_interval}s")
        print(f"[Orchestrator] Qwen Code: {self.qwen_command}")
        print(f"[Orchestrator] Monitoring: {self.needs_action}")
        print()
    
    def _find_qwen_command(self) -> str:
        """Find the Qwen Code command in PATH."""
        # Try common Qwen Code commands
        possible_commands = ['qwen', 'qwen.cmd', 'qwen-code', 'qwen_code']
        
        for cmd in possible_commands:
            try:
                # On Windows, use shell=True to find .cmd files
                import platform
                use_shell = platform.system() == 'Windows'
                
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=use_shell
                )
                if result.returncode == 0:
                    print(f"[Orchestrator] Found Qwen Code: {cmd} (v{result.stdout.strip()})")
                    return cmd
            except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
                continue
        
        # Default to 'qwen' - will fail gracefully if not found
        print("[Orchestrator] Warning: Qwen Code not found in PATH, using 'qwen' anyway")
        return 'qwen'
    
    def check_for_new_tasks(self) -> list:
        """
        Check Needs_Action folder for new task files.
        
        Returns:
            list: List of new task files to process
        """
        new_tasks = []
        
        try:
            for filepath in self.needs_action.iterdir():
                if filepath.is_file() and filepath.suffix == '.md':
                    if filepath.name not in self.processed_files:
                        # Check if file is being written to (skip if so)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read(10)  # Try to read first 10 chars
                            if content.strip():  # File has content
                                new_tasks.append(filepath)
                                self.processed_files.add(filepath.name)
                                print(f"[Orchestrator] New task detected: {filepath.name}")
                        except Exception as e:
                            # File is still being written, skip for now
                            print(f"[Orchestrator] Skipping file (being written): {filepath.name}")
                            continue
        except Exception as e:
            print(f"[Error] Checking for tasks: {e}")
        
        return new_tasks
    
    def build_qwen_prompt(self, task_files: list) -> str:
        """
        Build a comprehensive prompt for Qwen Code.
        
        Args:
            task_files: List of task files to process
            
        Returns:
            str: The prompt to give to Qwen Code
        """
        task_list = "\n".join([f"- `{f.name}`" for f in task_files])
        
        prompt = f"""# AI Employee Task Processing

You are the AI Employee reasoning engine powered by Qwen Code.

## Current Working Directory
{self.vault_path}

## Tasks to Process

Please process the following task files from /Needs_Action:

{task_list}

## Processing Instructions

For EACH task file:

1. **Read the action file** - Parse the YAML frontmatter and content
2. **Understand the task** - Identify what action is required
3. **Check Company_Handbook.md** - Follow the Rules of Engagement
4. **Create a plan** - Write a Plan.md file in /Plans/ with checkboxes
5. **Execute the plan** - Complete each step
6. **Update Dashboard.md** - Log the activity in the Recent Activity table
7. **Move to Done** - After completion, move the task file to /Done/

## Important Rules

- **Approval Required**: If an action requires human approval (see Company_Handbook.md approval thresholds), create a file in /Pending_Approval/ instead of acting directly
- **Logging**: Log all actions to /Logs/
- **Error Handling**: If you encounter an error, create an error log and move the file to a safe location

## Output Format

After processing, provide a summary:
- Tasks completed: [count]
- Tasks requiring approval: [count]
- Errors encountered: [count]

Begin processing now.
"""
        return prompt
    
    def trigger_qwen_code(self, task_files: list) -> bool:
        """
        Trigger Qwen Code to process the tasks.
        
        Args:
            task_files: List of task files to process
            
        Returns:
            bool: True if Qwen was triggered successfully
        """
        print(f"\n[Orchestrator] Triggering Qwen Code for {len(task_files)} task(s)...")
        
        # Build the prompt
        prompt = self.build_qwen_prompt(task_files)
        
        # Write prompt to a file for reference
        prompt_file = self.vault_path / '.last_qwen_prompt.md'
        prompt_file.write_text(prompt, encoding='utf-8')
        
        # Log the trigger
        self.log_event("qwen_triggered", {
            "task_count": len(task_files),
            "tasks": [f.name for f in task_files]
        })
        
        # Try to run Qwen Code
        try:
            print(f"[Orchestrator] Running: {self.qwen_command}")
            print(f"[Orchestrator] Working directory: {self.vault_path}")
            print("-" * 60)

            # Run Qwen Code with the prompt
            # Using subprocess to pipe the prompt to Qwen
            import platform
            use_shell = platform.system() == 'Windows'
            
            process = subprocess.Popen(
                [self.qwen_command],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=str(self.vault_path),
                shell=use_shell
            )

            # Send the prompt and get output
            output, _ = process.communicate(input=prompt, timeout=300)

            print(output)
            print("-" * 60)

            # Log completion
            self.log_event("qwen_completed", {
                "task_count": len(task_files),
                "output_length": len(output) if output else 0
            })

            print(f"[Orchestrator] Qwen Code processing complete")
            return True

        except FileNotFoundError:
            print(f"[Error] Qwen Code command not found: {self.qwen_command}")
            print(f"[Error] Please ensure Qwen Code is installed and in PATH")
            print(f"[Error] Try running: qwen --version")
            self.log_event("qwen_error", {"error": "Command not found", "command": self.qwen_command})
            return False

        except subprocess.TimeoutExpired:
            print(f"[Error] Qwen Code timed out after 300 seconds")
            process.kill()
            self.log_event("qwen_error", {"error": "Timeout", "timeout": 300})
            return False

        except Exception as e:
            print(f"[Error] Failed to run Qwen Code: {e}")
            self.log_event("qwen_error", {"error": str(e)})
            return False
    
    def log_event(self, event_type: str, details: dict):
        """
        Log an event to the Logs folder.
        
        Args:
            event_type: Type of event
            details: Event details dictionary
        """
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "details": details
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[Warning] Could not write log: {e}")
    
    def update_dashboard(self, tasks_processed: int):
        """
        Update the Dashboard.md with recent activity.
        
        Args:
            tasks_processed: Number of tasks processed
        """
        dashboard_file = self.vault_path / 'Dashboard.md'
        
        if not dashboard_file.exists():
            return
        
        try:
            content = dashboard_file.read_text(encoding='utf-8')
            
            # Update the "Completed Today" count
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
            activity_line = f"| {timestamp} | Batch processed {tasks_processed} task(s) | Complete |\n"
            
            # Find the Recent Activity table and add entry
            if "| Timestamp | Action | Status |" in content:
                # Insert after the header row
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if "| Timestamp | Action | Status |" in line:
                        # Insert after the separator row
                        if i + 1 < len(lines) and '|---' in lines[i + 1]:
                            lines.insert(i + 2, activity_line)
                            break
                
                content = '\n'.join(lines)
                dashboard_file.write_text(content, encoding='utf-8')
                print(f"[Orchestrator] Dashboard updated")
                
        except Exception as e:
            print(f"[Warning] Could not update dashboard: {e}")
    
    def run(self):
        """
        Main orchestration loop.
        """
        print("[Orchestrator] Starting AI Employee Orchestrator")
        print("[Orchestrator] Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                # Check for new tasks
                new_tasks = self.check_for_new_tasks()
                
                if new_tasks:
                    # Trigger Qwen Code to process tasks
                    success = self.trigger_qwen_code(new_tasks)
                    
                    if success:
                        # Update dashboard
                        self.update_dashboard(len(new_tasks))
                        
                        # Wait a bit for Qwen to finish file operations
                        print(f"[Orchestrator] Waiting for file operations to complete...")
                        time.sleep(5)
                
                # Wait for next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n[Orchestrator] Stopped by user")
        except Exception as e:
            print(f"[Orchestrator] Fatal error: {e}")
            raise


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Default to vault in project directory
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        print(f"No vault path specified, using default: {vault_path}")
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f"Error: Vault path does not exist: {vault_path}")
        sys.exit(1)
    
    orchestrator = Orchestrator(str(vault_path), check_interval=30)
    orchestrator.run()


if __name__ == '__main__':
    main()
