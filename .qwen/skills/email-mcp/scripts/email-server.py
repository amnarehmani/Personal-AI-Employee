#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Email Server - Send emails via SMTP.

Usage:
    python email-server.py send --to <email> --subject <subject> --body <body>
    python email-server.py draft --to <email> --subject <subject> --body <body>
    python email-server.py search --query <query>
"""

import argparse
import smtplib
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailServer:
    """Send emails via SMTP."""
    
    def __init__(self, vault_path: str = None):
        """Initialize email server."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'
        
        self.drafts = self.vault_path / 'Email_Drafts'
        self.drafts.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load email configuration from .env file."""
        env_file = Path(__file__).parent.parent.parent.parent / '.env'
        
        self.config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'smtp_username': os.getenv('SMTP_USERNAME', ''),
            'smtp_password': os.getenv('SMTP_PASSWORD', ''),
            'email_provider': os.getenv('EMAIL_PROVIDER', 'gmail'),
        }
        
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip()
    
    def send_email(self, to: str, subject: str, body: str, 
                   attachments: list = None, cc: list = None, 
                   bcc: list = None, dry_run: bool = False) -> dict:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            attachments: List of attachment paths
            cc: List of CC email addresses
            bcc: List of BCC email addresses
            dry_run: If True, don't actually send
            
        Returns:
            Result dictionary
        """
        result = {
            'success': False,
            'message': '',
            'timestamp': datetime.now().isoformat()
        }
        
        # Check configuration
        if not self.config['smtp_username'] or not self.config['smtp_password']:
            result['message'] = 'Email credentials not configured. Check .env file.'
            return result
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.config['smtp_username']
            msg['To'] = to
            msg['Subject'] = subject
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Add attachments
            if attachments:
                for filepath in attachments:
                    if os.path.exists(filepath):
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header(
                                'Content-Disposition',
                                f'attachment; filename={os.path.basename(filepath)}'
                            )
                            msg.attach(part)
                    else:
                        result['message'] = f'Attachment not found: {filepath}'
                        return result
            
            # Get all recipients
            all_recipients = [to]
            if cc:
                all_recipients.extend(cc)
            if bcc:
                all_recipients.extend(bcc)
            
            if dry_run:
                result['success'] = True
                result['message'] = f'Dry run: Would send to {", ".join(all_recipients)}'
                result['dry_run'] = True
            else:
                # Send email
                server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
                server.starttls()
                server.login(self.config['smtp_username'], self.config['smtp_password'])
                server.sendmail(self.config['smtp_username'], all_recipients, msg.as_string())
                server.quit()
                
                result['success'] = True
                result['message'] = f'Email sent to {to}'
        
        except Exception as e:
            result['message'] = f'Error: {str(e)}'
        
        # Log the action
        self.log_email_action('send', to, subject, result['success'])
        
        return result
    
    def create_draft(self, to: str, subject: str, body: str, 
                    attachments: list = None) -> Path:
        """
        Create an email draft.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text
            attachments: List of attachment paths
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now()
        filename = f"DRAFT_{subject.replace(' ', '_')[:20]}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.drafts / filename
        
        content = f"""---
type: email_draft
to: {to}
subject: {subject}
created: {timestamp.isoformat()}
status: draft
---

# Email Draft

## To
{to}

## Subject
{subject}

## Body
{body}

## Attachments
{', '.join(attachments) if attachments else 'None'}

---
*To send: Move to /Approved folder*
*To discard: Move to /Rejected folder*
"""
        
        filepath.write_text(content, encoding='utf-8')
        
        print(f"[Email] Draft created: {filename}")
        
        self.log_email_action('draft', to, subject, True)
        
        return filepath
    
    def search_emails(self, query: str, limit: int = 10) -> list:
        """
        Search emails (simulated - would use Gmail API in production).
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of matching emails
        """
        # In production, this would use Gmail API
        # For now, return a simulated response
        results = [{
            'id': 'simulated_1',
            'from': 'example@example.com',
            'subject': 'Simulated Result',
            'date': datetime.now().isoformat(),
            'snippet': 'This is a simulated search result. Configure Gmail API for real search.'
        }]
        
        self.log_email_action('search', query, '', True)
        
        return results
    
    def log_email_action(self, action: str, target: str, subject: str, success: bool):
        """Log email action to Logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.vault_path / 'Logs' / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': f'email_{action}',
            'target': target,
            'subject': subject,
            'success': success
        }
        
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"[Warning] Could not log email action: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Email Server')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # send command
    send_parser = subparsers.add_parser('send', help='Send email')
    send_parser.add_argument('--to', required=True, help='Recipient email')
    send_parser.add_argument('--subject', required=True, help='Email subject')
    send_parser.add_argument('--body', required=True, help='Email body')
    send_parser.add_argument('--attachments', help='Comma-separated attachment paths')
    send_parser.add_argument('--cc', help='CC emails (comma-separated)')
    send_parser.add_argument('--dry-run', action='store_true', help='Don\'t actually send')
    send_parser.add_argument('--vault', help='Vault path')
    
    # draft command
    draft_parser = subparsers.add_parser('draft', help='Create email draft')
    draft_parser.add_argument('--to', required=True, help='Recipient email')
    draft_parser.add_argument('--subject', required=True, help='Email subject')
    draft_parser.add_argument('--body', required=True, help='Email body')
    draft_parser.add_argument('--attachments', help='Comma-separated attachment paths')
    draft_parser.add_argument('--vault', help='Vault path')
    
    # search command
    search_parser = subparsers.add_parser('search', help='Search emails')
    search_parser.add_argument('--query', required=True, help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, help='Max results')
    search_parser.add_argument('--vault', help='Vault path')
    
    args = parser.parse_args()
    
    server = EmailServer(args.vault if hasattr(args, 'vault') else None)
    
    if args.command == 'send':
        attachments = [a.strip() for a in args.attachments.split(',')] if args.attachments else []
        cc = [c.strip() for c in args.cc.split(',')] if args.cc else None
        
        result = server.send_email(
            args.to, args.subject, args.body,
            attachments=attachments, cc=cc, dry_run=args.dry_run
        )
        
        if result['success']:
            print(f"[Email] {result['message']}")
        else:
            print(f"[Error] {result['message']}")
            sys.exit(1)
    
    elif args.command == 'draft':
        attachments = [a.strip() for a in args.attachments.split(',')] if args.attachments else []
        server.create_draft(args.to, args.subject, args.body, attachments=attachments)
    
    elif args.command == 'search':
        results = server.search_emails(args.query, args.limit)
        
        print(f"Search results for '{args.query}':")
        for email in results:
            print(f"  From: {email['from']}")
            print(f"  Subject: {email['subject']}")
            print(f"  Date: {email['date'][:16]}")
            print(f"  Snippet: {email['snippet']}")
            print()


if __name__ == '__main__':
    main()
