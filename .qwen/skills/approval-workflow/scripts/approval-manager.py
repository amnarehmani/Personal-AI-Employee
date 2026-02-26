#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Approval Manager - Manage human-in-the-loop approvals.

Usage:
    python approval-manager.py create --type <type> --action <action> --details <json>
    python approval-manager.py check --file <filename>
    python approval-manager.py list
    python approval-manager.py process
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta


class ApprovalManager:
    """Manage approval requests."""
    
    def __init__(self, vault_path: str = None):
        """Initialize approval manager."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'
        
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'
        
        # Ensure folders exist
        for folder in [self.pending_approval, self.approved, self.rejected]:
            folder.mkdir(parents=True, exist_ok=True)
    
    def create_approval(self, approval_type: str, action: str, details: dict, 
                       expires_hours: int = 24) -> Path:
        """
        Create an approval request file.
        
        Args:
            approval_type: Type of action (payment, email, etc.)
            action: Specific action name
            details: Dictionary with action details
            expires_hours: Hours until expiry
            
        Returns:
            Path to created file
        """
        timestamp = datetime.now()
        expiry = timestamp + timedelta(hours=expires_hours)
        
        # Generate filename
        safe_action = action.replace(' ', '_').upper()
        filename = f"{safe_action}_{timestamp.strftime('%Y-%m-%d_%H%M%S')}.md"
        filepath = self.pending_approval / filename
        
        # Build content
        content = f"""---
type: approval_request
action_type: {approval_type}
action: {action}
created: {timestamp.isoformat()}
expires: {expiry.isoformat()}
status: pending
---

# Approval Request: {approval_type.replace('_', ' ').title()}

## Action Details
"""
        
        # Add details
        for key, value in details.items():
            content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        content += f"""
## Instructions

**To Approve:**
Move this file to `/Approved` folder.

**To Reject:**
Move this file to `/Rejected` folder.

## Expiry
This request expires on: **{expiry.strftime('%Y-%m-%d %H:%M:%S')}**

---
*Created by Approval Workflow v0.1*
"""
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        
        print(f"[Approval] Created: {filename}")
        print(f"  Location: {filepath}")
        print(f"  Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return filepath
    
    def check_status(self, filename: str) -> str:
        """
        Check the status of an approval request.
        
        Args:
            filename: Name of the approval file
            
        Returns:
            Status string (pending, approved, rejected, expired, done)
        """
        # Check each folder
        folders = {
            'pending': self.pending_approval,
            'approved': self.approved,
            'rejected': self.rejected,
            'done': self.done
        }
        
        for status, folder in folders.items():
            filepath = folder / filename
            if filepath.exists():
                # Check for expiry if pending
                if status == 'pending':
                    content = filepath.read_text(encoding='utf-8')
                    if 'expires:' in content:
                        for line in content.split('\n'):
                            if 'expires:' in line:
                                try:
                                    expiry_str = line.split(':')[1].strip()
                                    expiry = datetime.fromisoformat(expiry_str)
                                    if datetime.now() > expiry:
                                        return 'expired'
                                except Exception:
                                    pass
                return status
        
        return 'not_found'
    
    def list_pending(self) -> list:
        """
        List all pending approval requests.
        
        Returns:
            List of pending approval file info
        """
        pending = []
        
        for filepath in self.pending_approval.iterdir():
            if filepath.is_file() and filepath.suffix == '.md':
                content = filepath.read_text(encoding='utf-8')
                
                # Extract key info
                info = {
                    'filename': filepath.name,
                    'type': 'Unknown',
                    'action': 'Unknown',
                    'created': 'Unknown',
                    'summary': ''
                }
                
                for line in content.split('\n'):
                    if line.startswith('action_type:'):
                        info['type'] = line.split(':')[1].strip()
                    elif line.startswith('action:'):
                        info['action'] = line.split(':')[1].strip()
                    elif line.startswith('created:'):
                        info['created'] = line.split(':')[1].strip()[:16]
                
                # Get summary from content
                if 'amount:' in content:
                    for line in content.split('\n'):
                        if 'amount:' in line.lower():
                            info['summary'] = line.split(':')[1].strip()
                            break
                
                pending.append(info)
        
        return pending
    
    def list_approved(self) -> list:
        """List all approved files ready for execution."""
        approved = []
        
        for filepath in self.approved.iterdir():
            if filepath.is_file() and filepath.suffix == '.md':
                approved.append({
                    'filename': filepath.name,
                    'path': str(filepath)
                })
        
        return approved
    
    def process_approved(self) -> list:
        """
        Process all approved files (move to Done after execution).
        
        Returns:
            List of processed files
        """
        processed = []
        
        for filepath in self.approved.iterdir():
            if filepath.is_file() and filepath.suffix == '.md':
                # In a real implementation, we would execute the action here
                # For now, just move to Done
                
                dest = self.done / filepath.name
                filepath.rename(dest)
                processed.append(filepath.name)
                
                print(f"[Approval] Processed: {filepath.name}")
        
        return processed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Approval Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # create command
    create_parser = subparsers.add_parser('create', help='Create approval request')
    create_parser.add_argument('--type', required=True, help='Action type')
    create_parser.add_argument('--action', required=True, help='Action name')
    create_parser.add_argument('--details', required=True, help='JSON details')
    create_parser.add_argument('--expires-hours', type=int, default=24, help='Expiry hours')
    create_parser.add_argument('--vault', help='Vault path')
    
    # check command
    check_parser = subparsers.add_parser('check', help='Check approval status')
    check_parser.add_argument('--file', required=True, help='Filename to check')
    check_parser.add_argument('--vault', help='Vault path')
    
    # list command
    list_parser = subparsers.add_parser('list', help='List pending approvals')
    list_parser.add_argument('--vault', help='Vault path')
    
    # process command
    process_parser = subparsers.add_parser('process', help='Process approved files')
    process_parser.add_argument('--vault', help='Vault path')
    
    args = parser.parse_args()
    
    manager = ApprovalManager(args.vault if hasattr(args, 'vault') else None)
    
    if args.command == 'create':
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON details: {e}")
            sys.exit(1)
        
        manager.create_approval(args.type, args.action, details, args.expires_hours)
    
    elif args.command == 'check':
        status = manager.check_status(args.file)
        print(f"Status: {status}")
    
    elif args.command == 'list':
        pending = manager.list_pending()
        
        if pending:
            print("Pending Approvals:")
            for i, item in enumerate(pending, 1):
                print(f"  {i}. {item['filename']}")
                print(f"     Type: {item['type']} | Action: {item['action']}")
                print(f"     Created: {item['created']}")
                if item['summary']:
                    print(f"     Summary: {item['summary']}")
                print()
        else:
            print("No pending approvals")
    
    elif args.command == 'process':
        processed = manager.process_approved()
        if processed:
            print(f"Processed {len(processed)} file(s)")
        else:
            print("No approved files to process")


if __name__ == '__main__':
    main()
