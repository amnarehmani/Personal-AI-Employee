#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scheduler - Schedule and run recurring tasks.

Usage:
    python scheduler.py run              # Run scheduled tasks (called by cron/Task Scheduler)
    python scheduler.py list             # List scheduled tasks
    python scheduler.py setup-windows    # Set up Windows Task Scheduler
    python scheduler.py setup-cron       # Set up cron job (Linux/Mac)
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime


class Scheduler:
    """Schedule and run recurring tasks."""
    
    def __init__(self, vault_path: str = None):
        """Initialize scheduler."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
        
        # Define scheduled tasks
        self.tasks = [
            {
                'name': 'daily_briefing',
                'schedule': '08:00',  # 8:00 AM daily
                'description': 'Generate daily briefing',
                'script': 'tasks/daily_briefing.py'
            },
            {
                'name': 'process_pending',
                'schedule': '*/30',  # Every 30 minutes
                'description': 'Process pending tasks',
                'command': 'python orchestrator.py AI_Employee_Vault'
            },
            {
                'name': 'weekly_audit',
                'schedule': 'Sunday 22:00',  # Sunday 10:00 PM
                'description': 'Weekly business audit',
                'script': 'tasks/weekly_audit.py'
            },
            {
                'name': 'update_dashboard',
                'schedule': '*/15',  # Every 15 minutes
                'description': 'Update dashboard stats',
                'command': 'python update_dashboard.py AI_Employee_Vault'
            }
        ]
    
    def run_task(self, task: dict) -> dict:
        """
        Run a scheduled task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Result dictionary
        """
        result = {
            'task': task['name'],
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'output': ''
        }
        
        try:
            if 'script' in task:
                # Run Python script
                script_path = Path(__file__).parent / task['script']
                if script_path.exists():
                    proc = subprocess.run(
                        ['python', str(script_path)],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    result['output'] = proc.stdout
                    result['success'] = proc.returncode == 0
                    if not result['success']:
                        result['error'] = proc.stderr
                else:
                    result['error'] = f'Script not found: {script_path}'
            
            elif 'command' in task:
                # Run shell command
                proc = subprocess.run(
                    task['command'],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                result['output'] = proc.stdout
                result['success'] = proc.returncode == 0
                if not result['success']:
                    result['error'] = proc.stderr
            
            else:
                result['error'] = 'No script or command specified'
        
        except subprocess.TimeoutExpired:
            result['error'] = 'Task timed out after 300 seconds'
        except Exception as e:
            result['error'] = str(e)
        
        # Log result
        self.log_task_run(task['name'], result)
        
        return result
    
    def run_due_tasks(self) -> list:
        """Run all tasks that are due."""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        current_day = now.strftime('%A')
        
        results = []
        
        for task in self.tasks:
            schedule = task['schedule']
            should_run = False
            
            # Check if task is due
            if schedule.startswith('*/'):
                # Interval-based (e.g., */30 = every 30 minutes)
                interval = int(schedule[2:])
                minute = now.minute
                if minute % interval == 0:
                    should_run = True
            
            elif ' ' in schedule:
                # Day and time (e.g., "Sunday 22:00")
                day, time = schedule.split(' ')
                if day.lower() == current_day.lower() and time == current_time:
                    should_run = True
            
            else:
                # Time only (e.g., "08:00")
                if schedule == current_time:
                    should_run = True
            
            if should_run:
                print(f"[Scheduler] Running task: {task['name']}")
                result = self.run_task(task)
                results.append(result)
                
                if result['success']:
                    print(f"[Scheduler] Task completed: {task['name']}")
                else:
                    print(f"[Scheduler] Task failed: {task['name']} - {result.get('error', 'Unknown error')}")
        
        return results
    
    def list_tasks(self):
        """List all scheduled tasks."""
        print("Scheduled Tasks:")
        print("=" * 60)
        
        for task in self.tasks:
            print(f"\n  Task: {task['name']}")
            print(f"  Schedule: {task['schedule']}")
            print(f"  Description: {task['description']}")
            if 'script' in task:
                print(f"  Script: {task['script']}")
            elif 'command' in task:
                print(f"  Command: {task['command']}")
    
    def setup_windows_task(self):
        """Set up Windows Task Scheduler."""
        scheduler_path = Path(__file__).resolve()
        project_root = scheduler_path.parent.parent
        
        print("Setting up Windows Task Scheduler...")
        print()
        
        # Create daily briefing task
        cmd = f'schtasks /create /tn "AI_Employee_DailyBriefing" /tr "python {scheduler_path} run" /sc daily /st 08:00 /sd "{project_root}"'
        
        print(f"Run this command in PowerShell (as Administrator):")
        print(f"  {cmd}")
        print()
        print("Or create tasks manually:")
        print("  1. Open Task Scheduler")
        print("  2. Create Basic Task")
        print("  3. Name: AI_Employee_DailyBriefing")
        print("  4. Trigger: Daily at 8:00 AM")
        print("  5. Action: Start a program")
        print(f"  6. Program: python")
        print(f"  7. Arguments: {scheduler_path} run")
        print(f"  8. Start in: {project_root}")
    
    def setup_cron(self):
        """Set up cron job (Linux/Mac)."""
        scheduler_path = Path(__file__).resolve()
        project_root = scheduler_path.parent.parent
        
        print("Setting up cron job...")
        print()
        print("Add this line to your crontab (run 'crontab -e'):")
        print()
        print(f"  0 8 * * * cd {project_root} && python {scheduler_path} run")
        print(f"  */30 * * * * cd {project_root} && python {scheduler_path} run")
        print()
        print("This will:")
        print("  - Run daily briefing at 8:00 AM")
        print("  - Run task processing every 30 minutes")
    
    def log_task_run(self, task_name: str, result: dict):
        """Log task execution."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': f'scheduler_{task_name}',
            'result': result
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[Warning] Could not log task: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Scheduler')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # run command
    subparsers.add_parser('run', help='Run scheduled tasks')
    
    # list command
    subparsers.add_parser('list', help='List scheduled tasks')
    
    # setup-windows command
    subparsers.add_parser('setup-windows', help='Set up Windows Task Scheduler')
    
    # setup-cron command
    subparsers.add_parser('setup-cron', help='Set up cron job')
    
    args = parser.parse_args()
    
    scheduler = Scheduler()
    
    if args.command == 'run':
        results = scheduler.run_due_tasks()
        if results:
            print(f"\n[Scheduler] Ran {len(results)} task(s)")
        else:
            print("\n[Scheduler] No tasks due at this time")
    
    elif args.command == 'list':
        scheduler.list_tasks()
    
    elif args.command == 'setup-windows':
        scheduler.setup_windows_task()
    
    elif args.command == 'setup-cron':
        scheduler.setup_cron()


if __name__ == '__main__':
    main()
