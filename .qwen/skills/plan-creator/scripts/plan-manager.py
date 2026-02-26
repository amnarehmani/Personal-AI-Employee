#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Plan Manager - Create and manage structured plans.

Usage:
    python plan-manager.py create --objective "<obj>" --steps "<step1>,<step2>"
    python plan-manager.py update --file <file> --step <n> --status <status>
    python plan-manager.py status --file <file>
    python plan-manager.py list
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime


class PlanManager:
    """Manage task plans."""
    
    def __init__(self, vault_path: str = None):
        """Initialize plan manager."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'
        
        self.plans_folder = self.vault_path / 'Plans'
        self.done = self.vault_path / 'Done'
        
        # Ensure folders exist
        self.plans_folder.mkdir(parents=True, exist_ok=True)
        self.done.mkdir(parents=True, exist_ok=True)
    
    def create_plan(self, objective: str, steps: list, priority: str = 'normal',
                   context: dict = None) -> Path:
        """
        Create a new plan.
        
        Args:
            objective: What the plan aims to achieve
            steps: List of step descriptions
            priority: Priority level (high, normal, low)
            context: Additional context dictionary
            
        Returns:
            Path to created plan file
        """
        timestamp = datetime.now()
        
        # Generate filename
        safe_objective = objective.replace(' ', '_')[:30]
        filename = f"PLAN_{safe_objective}_{timestamp.strftime('%Y-%m-%d_%H%M%S')}.md"
        filepath = self.plans_folder / filename
        
        # Build steps markdown
        steps_md = ""
        for i, step in enumerate(steps, 1):
            steps_md += f"- [ ] {i}. {step}\n"
        
        # Build context section
        context_md = ""
        if context:
            context_md = "## Context\n"
            for key, value in context.items():
                context_md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            context_md += "\n"
        
        # Build content
        content = f"""---
type: plan
objective: {objective}
created: {timestamp.isoformat()}
status: in_progress
priority: {priority}
---

# Plan: {objective}

{context_md}## Steps
{steps_md}
## Notes

*Add notes during execution*

## Timeline
- Started: {timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')}
- Target: {(timestamp.replace(hour=23, minute=59)).strftime('%Y-%m-%dT%H:%M:%SZ')}

---
*Created by Plan Creator v0.1*
"""
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        
        print(f"[Plan] Created: {filename}")
        print(f"  Objective: {objective}")
        print(f"  Steps: {len(steps)}")
        print(f"  Priority: {priority}")
        
        return filepath
    
    def update_step(self, filename: str, step_number: int, status: str,
                   note: str = None) -> bool:
        """
        Update a step's status.
        
        Args:
            filename: Plan file name
            step_number: Step number (1-indexed)
            status: Status (completed, failed, skipped)
            note: Optional note to add
            
        Returns:
            True if successful
        """
        # Find the file
        filepath = self._find_file(filename)
        if not filepath:
            print(f"[Error] Plan not found: {filename}")
            return False
        
        content = filepath.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Find and update the step
        step_found = False
        for i, line in enumerate(lines):
            if line.strip().startswith(f'- [ ] {step_number}.') or \
               line.strip().startswith(f'- [x] {step_number}.'):
                # Determine checkbox based on status
                if status == 'completed':
                    checkbox = '[x]'
                elif status == 'failed':
                    checkbox = '[-]'
                else:
                    checkbox = '[ ]'
                
                # Get step text
                step_text = line.split('.', 1)[1].strip() if '.' in line else line
                
                # Replace line
                lines[i] = f"- {checkbox} {step_number}. {step_text}"
                step_found = True
                
                # Add note if provided
                if note:
                    lines.insert(i + 1, f"  *Note: {note}*")
                break
        
        if not step_found:
            print(f"[Error] Step {step_number} not found")
            return False
        
        # Update status in frontmatter if all steps complete
        completed = sum(1 for l in lines if '- [x]' in l)
        total = sum(1 for l in lines if '- [' in l and '.' in l)
        
        if completed == total and total > 0:
            # All steps complete, update status
            for i, line in enumerate(lines):
                if line.startswith('status:'):
                    lines[i] = 'status: completed'
                    break
        
        # Write updated content
        filepath.write_text('\n'.join(lines), encoding='utf-8')
        
        print(f"[Plan] Updated step {step_number}: {status}")
        return True
    
    def get_status(self, filename: str) -> dict:
        """
        Get plan status.
        
        Args:
            filename: Plan file name
            
        Returns:
            Status dictionary
        """
        filepath = self._find_file(filename)
        if not filepath:
            return {'error': 'Plan not found'}
        
        content = filepath.read_text(encoding='utf-8')
        
        # Extract info
        status = {
            'filename': filename,
            'objective': 'Unknown',
            'status': 'Unknown',
            'priority': 'Unknown',
            'created': 'Unknown',
            'total_steps': 0,
            'completed_steps': 0,
            'steps': []
        }
        
        lines = content.split('\n')
        in_steps = False
        
        for line in lines:
            if line.startswith('objective:'):
                status['objective'] = line.split(':', 1)[1].strip()
            elif line.startswith('status:'):
                status['status'] = line.split(':', 1)[1].strip()
            elif line.startswith('priority:'):
                status['priority'] = line.split(':', 1)[1].strip()
            elif line.startswith('created:'):
                status['created'] = line.split(':', 1)[1].strip()[:16]
            elif '- [' in line and '.' in line:
                in_steps = True
                status['total_steps'] += 1
                if '- [x]' in line:
                    status['completed_steps'] += 1
                status['steps'].append(line.strip())
        
        # Calculate progress
        if status['total_steps'] > 0:
            progress = (status['completed_steps'] / status['total_steps']) * 100
            status['progress'] = f"{progress:.0f}%"
        else:
            status['progress'] = 'N/A'
        
        return status
    
    def list_plans(self, status_filter: str = None) -> list:
        """
        List plans.
        
        Args:
            status_filter: Filter by status (in_progress, completed)
            
        Returns:
            List of plan info
        """
        plans = []
        
        for filepath in self.plans_folder.iterdir():
            if filepath.is_file() and filepath.suffix == '.md':
                status = self.get_status(filepath.name)
                
                if status_filter and status.get('status') != status_filter:
                    continue
                
                plans.append(status)
        
        return plans
    
    def complete_plan(self, filename: str) -> bool:
        """Move completed plan to Done folder."""
        filepath = self._find_file(filename)
        if not filepath:
            return False
        
        dest = self.done / filename
        filepath.rename(dest)
        print(f"[Plan] Completed: {filename}")
        return True
    
    def _find_file(self, filename: str) -> Path:
        """Find a plan file by name."""
        # Try exact name first
        filepath = self.plans_folder / filename
        if filepath.exists():
            return filepath
        
        # Try without .md extension
        if not filename.endswith('.md'):
            filepath = self.plans_folder / f"{filename}.md"
            if filepath.exists():
                return filepath
        
        return None


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Plan Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create new plan')
    create_parser.add_argument('--objective', required=True, help='Plan objective')
    create_parser.add_argument('--steps', required=True, help='Comma-separated steps')
    create_parser.add_argument('--priority', default='normal', help='Priority level')
    create_parser.add_argument('--context', help='JSON context')
    create_parser.add_argument('--vault', help='Vault path')
    
    # update command
    update_parser = subparsers.add_parser('update', help='Update plan step')
    update_parser.add_argument('--file', required=True, help='Plan filename')
    update_parser.add_argument('--step', type=int, required=True, help='Step number')
    update_parser.add_argument('--status', required=True, help='Step status')
    update_parser.add_argument('--note', help='Optional note')
    update_parser.add_argument('--vault', help='Vault path')
    
    # status command
    status_parser = subparsers.add_parser('status', help='Get plan status')
    status_parser.add_argument('--file', required=True, help='Plan filename')
    status_parser.add_argument('--vault', help='Vault path')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List plans')
    list_parser.add_argument('--status', help='Filter by status')
    list_parser.add_argument('--vault', help='Vault path')
    
    args = parser.parse_args()
    
    manager = PlanManager(args.vault if hasattr(args, 'vault') else None)
    
    if args.command == 'create':
        steps = [s.strip() for s in args.steps.split(',')]
        context = json.loads(args.context) if args.context else None
        manager.create_plan(args.objective, steps, args.priority, context)
    
    elif args.command == 'update':
        manager.update_step(args.file, args.step, args.status, args.note)
    
    elif args.command == 'status':
        status = manager.get_status(args.file)
        
        if 'error' in status:
            print(f"Error: {status['error']}")
        else:
            print(f"Plan: {status['objective']}")
            print(f"Status: {status['status']}")
            print(f"Priority: {status['priority']}")
            print(f"Progress: {status['completed_steps']}/{status['total_steps']} steps ({status['progress']})")
            print()
            print("Steps:")
            for step in status['steps']:
                print(f"  {step}")
    
    elif args.command == 'list':
        plans = manager.list_plans(args.status if hasattr(args, 'status') else None)
        
        if plans:
            print(f"Found {len(plans)} plan(s):")
            print()
            for plan in plans:
                print(f"  {plan['filename']}")
                print(f"    Objective: {plan['objective']}")
                print(f"    Status: {plan['status']} | Progress: {plan['progress']}")
                print()
        else:
            print("No plans found")


if __name__ == '__main__':
    main()
