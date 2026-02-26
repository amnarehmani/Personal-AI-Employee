#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitor Gmail for new important emails.

Usage:
    python gmail-watcher.py              # Run watcher
    python gmail-watcher.py --test       # Test connection
    python gmail-watcher.py --status     # Show status
    python gmail-watcher.py --clear-cache  # Clear processed cache
"""

import argparse
import base64
import json
import os
import sys
import pickle
from pathlib import Path
from datetime import datetime
from email import message_from_bytes

# Try to import Google API libraries
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class GmailWatcher:
    """Watch Gmail for new important emails."""
    
    # Scopes for Gmail API
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str = None, check_interval: int = 300):
        """
        Initialize Gmail watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            check_interval: Seconds between checks (default: 5 min)
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'
        
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        self.check_interval = check_interval
        
        # Paths for credentials
        self.credentials_path = Path(__file__).parent.parent.parent.parent / 'credentials.json'
        self.token_path = Path(__file__).parent.parent.parent.parent / 'token.json'
        
        # Processed email IDs cache
        self.processed_ids_file = Path(__file__).parent / '.processed_emails.json'
        self.processed_ids = self._load_processed_ids()
        
        # Keywords to watch for
        self.keywords = ['urgent', 'invoice', 'payment', 'asap', 'important', 'help']
        
        # VIP senders (add your important contacts)
        self.vip_senders = []
        
        # Gmail service
        self.service = None
    
    def _load_processed_ids(self) -> set:
        """Load set of processed email IDs."""
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get('ids', []))
            except Exception:
                pass
        return set()
    
    def _save_processed_ids(self):
        """Save processed email IDs to cache."""
        # Keep only last 1000 IDs to prevent unbounded growth
        ids_list = list(self.processed_ids)[-1000:]
        
        with open(self.processed_ids_file, 'w') as f:
            json.dump({'ids': ids_list, 'updated': datetime.now().isoformat()}, f)
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API.
        
        Returns:
            True if authentication successful
        """
        if not GOOGLE_AVAILABLE:
            print("[Error] Google API libraries not installed")
            print("Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
            return False
        
        creds = None
        
        # Load token if exists
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"[Error] Token refresh failed: {e}")
                    return False
            else:
                if not self.credentials_path.exists():
                    print(f"[Error] credentials.json not found at: {self.credentials_path}")
                    print("Download from Google Cloud Console")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"[Error] Authentication failed: {e}")
                    return False
            
            # Save token
            with open(self.token_path, 'w') as f:
                f.write(creds.to_json())
        
        # Build service
        self.service = build('gmail', 'v1', credentials=creds)
        return True
    
    def check_for_updates(self) -> list:
        """
        Check Gmail for new important emails.
        
        Returns:
            List of new email messages
        """
        if not self.service:
            return []
        
        new_emails = []
        
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()
            
            messages = results.get('messages', [])
            
            for msg in messages:
                msg_id = msg['id']
                
                # Skip if already processed
                if msg_id in self.processed_ids:
                    continue
                
                # Get full message
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                
                # Check if email matches criteria
                if self._is_important(message):
                    new_emails.append(message)
                    self.processed_ids.add(msg_id)
            
            # Save processed IDs
            self._save_processed_ids()
            
        except Exception as e:
            print(f"[Error] Checking Gmail: {e}")
        
        return new_emails
    
    def _is_important(self, message: dict) -> bool:
        """
        Check if email is important.
        
        Args:
            message: Gmail message dict
            
        Returns:
            True if email is important
        """
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        from_email = headers.get('From', '')
        subject = headers.get('Subject', '')
        
        # Check VIP senders
        for vip in self.vip_senders:
            if vip.lower() in from_email.lower():
                return True
        
        # Check keywords
        text = f"{subject} {from_email}".lower()
        for keyword in self.keywords:
            if keyword.lower() in text:
                return True
        
        # Check for important label
        labels = message.get('labelIds', [])
        if 'IMPORTANT' in labels:
            return True
        
        # Check for attachments
        if self._has_attachments(message['payload']):
            return True
        
        return False
    
    def _has_attachments(self, part: dict) -> bool:
        """Check if message part has attachments."""
        if part.get('filename') and part['filename']:
            return True
        
        for child in part.get('parts', []):
            if self._has_attachments(child):
                return True
        
        return False
    
    def _decode_body(self, message: dict) -> str:
        """Decode email body."""
        def get_body(part):
            if part['mimeType'] == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            
            for child in part.get('parts', []):
                body = get_body(child)
                if body:
                    return body
            
            return ''
        
        return get_body(message['payload'])
    
    def create_action_file(self, message: dict) -> Path:
        """
        Create action file for email.
        
        Args:
            message: Gmail message dict
            
        Returns:
            Path to created file
        """
        headers = {h['name']: h['value'] for h in message['payload']['headers']}
        
        from_email = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')
        received = headers.get('Date', '')
        msg_id = message['id']
        
        # Decode body
        body = self._decode_body(message)[:1000]  # Limit to 1000 chars
        
        # Generate filename
        safe_subject = subject.replace(' ', '_').replace(':', '')[:30]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"GMAIL_{safe_subject}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        # Build content
        content = f"""---
type: gmail_email
from: {from_email}
subject: {subject}
received: {received}
message_id: {msg_id}
priority: high
status: pending
---

# Gmail Message

## From
{from_email}

## Subject
{subject}

## Received
{received}

## Content

{body}

## Suggested Actions

- [ ] Read and understand email
- [ ] Draft appropriate response
- [ ] Take required action
- [ ] Mark as processed

---
*Created by Gmail Watcher v0.1*
"""
        
        filepath.write_text(content, encoding='utf-8')
        
        return filepath
    
    def run(self):
        """Run the Gmail watcher."""
        import time
        
        print("[Gmail Watcher] Starting...")
        print(f"[Gmail Watcher] Vault: {self.vault_path}")
        print(f"[Gmail Watcher] Check interval: {self.check_interval}s")
        
        # Authenticate
        if not self.authenticate():
            print("[Gmail Watcher] Authentication failed. Exiting.")
            return
        
        print("[Gmail Watcher] Authenticated successfully")
        print(f"[Gmail Watcher] Watching for emails with keywords: {', '.join(self.keywords)}")
        print()
        
        try:
            while True:
                emails = self.check_for_updates()
                
                for email in emails:
                    filepath = self.create_action_file(email)
                    print(f"[Gmail Watcher] Created action file: {filepath.name}")
                
                if emails:
                    print(f"[Gmail Watcher] Found {len(emails)} new email(s)")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n[Gmail Watcher] Stopped by user")
        except Exception as e:
            print(f"[Gmail Watcher] Error: {e}")
    
    def test_connection(self) -> bool:
        """Test Gmail API connection."""
        if not self.authenticate():
            return False
        
        try:
            # Get profile
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"[Gmail Watcher] Connected to: {profile['emailAddress']}")
            return True
        except Exception as e:
            print(f"[Gmail Watcher] Connection test failed: {e}")
            return False
    
    def show_status(self):
        """Show watcher status."""
        print("Gmail Watcher Status:")
        print(f"  Processed emails: {len(self.processed_ids)}")
        print(f"  Keywords: {', '.join(self.keywords)}")
        print(f"  VIP senders: {', '.join(self.vip_senders) if self.vip_senders else 'None configured'}")
        print(f"  Check interval: {self.check_interval}s")
        print(f"  Cache file: {self.processed_ids_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gmail Watcher')
    parser.add_argument('--vault', help='Vault path')
    parser.add_argument('--interval', type=int, default=300, help='Check interval (seconds)')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--clear-cache', action='store_true', help='Clear processed cache')
    
    args = parser.parse_args()
    
    watcher = GmailWatcher(args.vault, args.interval)
    
    if args.test:
        success = watcher.test_connection()
        sys.exit(0 if success else 1)
    
    elif args.status:
        watcher.show_status()
    
    elif args.clear_cache:
        if watcher.processed_ids_file.exists():
            watcher.processed_ids_file.unlink()
            print("[Gmail Watcher] Cache cleared")
        else:
            print("[Gmail Watcher] No cache to clear")
    
    else:
        watcher.run()


if __name__ == '__main__':
    main()
