#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Watcher - Monitor Gmail for new important emails.
Silver Tier Implementation - Fully functional with credentials.json

Usage:
    python gmail_watcher.py              # Run watcher continuously
    python gmail_watcher.py --auth       # First-time authentication
    python gmail_watcher.py --test       # Test connection
    python gmail_watcher.py --once       # Run once (for scheduler)
"""

import argparse
import base64
import json
import os
import sys
import pickle
import time
from pathlib import Path
from datetime import datetime

# Google API imports
try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError as e:
    GOOGLE_AVAILABLE = False
    print(f"[Warning] Google API libraries not installed: {e}")
    print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")


class GmailWatcher:
    """
    Watch Gmail for new important emails and create action files.
    
    Silver Tier Implementation:
    - Monitors Gmail API for unread/important emails
    - Creates action files in Needs_Action folder
    - Tracks processed emails to avoid duplicates
    - Supports keywords and VIP sender filtering
    """
    
    # Gmail API Scopes
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self, vault_path: str = None, check_interval: int = 120):
        """
        Initialize Gmail Watcher.
        
        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between checks (default: 2 min)
        """
        # Set vault path
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        
        self.needs_action = self.vault_path / 'Needs_Action'
        self.needs_action.mkdir(parents=True, exist_ok=True)
        
        self.check_interval = check_interval
        
        # Paths for credentials (relative to project root)
        self.project_root = Path(__file__).parent.parent
        self.credentials_path = self.project_root / 'credentials.json'
        self.token_path = self.project_root / 'token.json'
        
        # Processed email IDs cache
        self.processed_ids_file = Path(__file__).parent / '.gmail_processed.json'
        self.processed_ids = self._load_processed_ids()
        
        # Watcher configuration
        self.keywords = ['urgent', 'invoice', 'payment', 'asap', 'important', 'help', 'action required']
        self.vip_senders = []  # Add your VIP senders
        self.max_results = 10  # Max emails to fetch per check
        
        # Gmail service
        self.service = None
        self.authenticated = False
    
    def _load_processed_ids(self) -> set:
        """Load set of processed email IDs from cache."""
        if self.processed_ids_file.exists():
            try:
                with open(self.processed_ids_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return set(data.get('ids', []))
            except Exception:
                pass
        return set()
    
    def _save_processed_ids(self):
        """Save processed email IDs to cache file."""
        # Keep only last 1000 IDs to prevent unbounded growth
        ids_list = list(self.processed_ids)[-1000:]
        
        with open(self.processed_ids_file, 'w', encoding='utf-8') as f:
            json.dump({
                'ids': ids_list,
                'updated': datetime.now().isoformat(),
                'count': len(ids_list)
            }, f, indent=2)
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0.
        
        Returns:
            True if authentication successful
        """
        if not GOOGLE_AVAILABLE:
            print("[Error] Google API libraries not installed")
            return False
        
        # Check credentials file exists
        if not self.credentials_path.exists():
            print(f"[Error] credentials.json not found at: {self.credentials_path}")
            print("Please create a project in Google Cloud Console and download credentials.json")
            return False
        
        creds = None
        
        # Load existing token
        if self.token_path.exists():
            try:
                creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)
            except Exception as e:
                print(f"[Warning] Could not load token: {e}")
                self.token_path.unlink()
        
        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                    print("[Auth] Token refreshed successfully")
                except Exception as e:
                    print(f"[Auth] Token refresh failed: {e}")
                    creds = None
            
            if not creds:
                print("[Auth] Starting OAuth flow...")
                print(f"[Auth] Using credentials: {self.credentials_path}")
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, self.SCOPES
                    )
                    creds = flow.run_local_server(port=0, host='localhost')
                    print("[Auth] Authentication successful!")
                except Exception as e:
                    print(f"[Error] Authentication failed: {e}")
                    return False
            
            # Save token for future use
            try:
                with open(self.token_path, 'w', encoding='utf-8') as f:
                    f.write(creds.to_json())
                print(f"[Auth] Token saved to: {self.token_path}")
            except Exception as e:
                print(f"[Warning] Could not save token: {e}")
        
        # Build Gmail service
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.authenticated = True
            
            # Verify access
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"[Auth] Connected to: {profile['emailAddress']}")
            
            return True
            
        except Exception as e:
            print(f"[Error] Could not build Gmail service: {e}")
            return False
    
    def check_for_updates(self) -> list:
        """
        Check Gmail for new important emails.
        
        Returns:
            List of new email message dicts
        """
        if not self.service:
            return []
        
        new_emails = []
        
        try:
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=self.max_results
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
                
                # Check if email matches criteria (important, keywords, VIP, etc.)
                if self._is_important(message):
                    new_emails.append(message)
                    self.processed_ids.add(msg_id)
            
            # Save processed IDs
            if new_emails:
                self._save_processed_ids()
            
        except HttpError as e:
            if e.resp.status == 401:
                print("[Error] Authentication expired. Re-authenticating...")
                self.authenticate()
            else:
                print(f"[Error] Gmail API error: {e}")
        except Exception as e:
            print(f"[Error] Checking Gmail: {e}")
        
        return new_emails
    
    def _is_important(self, message: dict) -> bool:
        """
        Check if email is important based on criteria.
        
        Args:
            message: Gmail message dict
            
        Returns:
            True if email should trigger action file
        """
        headers = {h['name'].lower(): h['value'] for h in message['payload']['headers']}
        
        from_email = headers.get('from', '')
        subject = headers.get('subject', '')
        
        # Check VIP senders
        for vip in self.vip_senders:
            if vip.lower() in from_email.lower():
                return True
        
        # Check keywords in subject and from
        text = f"{subject} {from_email}".lower()
        for keyword in self.keywords:
            if keyword.lower() in text:
                return True
        
        # Check for important label
        labels = message.get('labelIds', [])
        if 'IMPORTANT' in labels or 'INBOX' in labels:
            return True
        
        # Check for attachments (might be invoices, documents, etc.)
        if self._has_attachments(message['payload']):
            return True
        
        return False
    
    def _has_attachments(self, part: dict) -> bool:
        """Check if message part has attachments."""
        if part.get('filename') and part['filename'].strip():
            return True
        
        for child in part.get('parts', []):
            if self._has_attachments(child):
                return True
        
        return False
    
    def _decode_body(self, message: dict) -> str:
        """Decode email body text."""
        def get_body(part):
            if part['mimeType'] == 'text/plain':
                data = part.get('body', {}).get('data', '')
                if data:
                    try:
                        return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    except Exception:
                        pass
            
            for child in part.get('parts', []):
                body = get_body(child)
                if body:
                    return body
            
            return ''
        
        return get_body(message['payload'])
    
    def create_action_file(self, message: dict) -> Path:
        """
        Create action file for email in Needs_Action folder.
        
        Args:
            message: Gmail message dict
            
        Returns:
            Path to created action file
        """
        headers = {h['name'].lower(): h['value'] for h in message['payload']['headers']}
        
        from_email = headers.get('from', 'Unknown')
        subject = headers.get('subject', 'No Subject')
        received = headers.get('date', '')
        msg_id = message['id']
        
        # Decode body (limit to 2000 chars)
        body = self._decode_body(message)[:2000]
        
        # Generate filename
        safe_subject = subject.replace(' ', '_').replace(':', '').replace('/', '_')[:40]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"GMAIL_{safe_subject}_{timestamp}.md"
        filepath = self.needs_action / filename
        
        # Determine priority
        priority = 'high' if any(kw in subject.lower() for kw in ['urgent', 'asap', 'emergency']) else 'normal'
        
        # Build action file content
        content = f"""---
type: gmail_email
from: {from_email}
subject: {subject}
received: {received}
message_id: {msg_id}
priority: {priority}
status: pending
---

# Gmail Message

## From
**{from_email}**

## Subject
{subject}

## Received
{received}

## Message Content

{body if body else '*No text content*'}

## Suggested Actions

- [ ] Read and understand the email
- [ ] Draft appropriate response
- [ ] Take required action
- [ ] Mark email as read in Gmail
- [ ] Move this file to /Done when complete

---
*Created by Gmail Watcher v0.1 (Silver Tier)*
*Message ID: {msg_id}*
"""
        
        filepath.write_text(content, encoding='utf-8')
        
        return filepath
    
    def run(self):
        """Run the Gmail Watcher continuously."""
        print("=" * 60)
        print("Gmail Watcher v0.1 - Silver Tier")
        print("=" * 60)
        print(f"[Watcher] Vault: {self.vault_path}")
        print(f"[Watcher] Check interval: {self.check_interval}s")
        print(f"[Watcher] Keywords: {', '.join(self.keywords)}")
        print(f"[Watcher] VIP senders: {', '.join(self.vip_senders) if self.vip_senders else 'None'}")
        print()
        
        # Authenticate
        if not self.authenticate():
            print("[Error] Authentication failed. Exiting.")
            return
        
        print()
        print("[Watcher] Monitoring Gmail for new important emails...")
        print("[Watcher] Press Ctrl+C to stop")
        print()
        
        try:
            while True:
                emails = self.check_for_updates()
                
                for email in emails:
                    filepath = self.create_action_file(email)
                    headers = {h['name'].lower(): h['value'] for h in email['payload']['headers']}
                    print(f"[Watcher] New email from {headers.get('from', 'Unknown')[:50]}")
                    print(f"          Action file: {filepath.name}")
                
                if emails:
                    print(f"[Watcher] Found {len(emails)} new email(s)")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            print("\n[Watcher] Stopped by user")
        except Exception as e:
            print(f"[Error] Watcher error: {e}")
    
    def run_once(self) -> int:
        """
        Run once and check for new emails (for scheduler).
        
        Returns:
            Number of new emails found
        """
        if not self.authenticated and not self.authenticate():
            return 0
        
        emails = self.check_for_updates()
        
        for email in emails:
            filepath = self.create_action_file(email)
            headers = {h['name'].lower(): h['value'] for h in email['payload']['headers']}
            print(f"[Watcher] New email: {filepath.name}")
        
        print(f"[Watcher] Found {len(emails)} new email(s)")
        return len(emails)
    
    def test_connection(self) -> bool:
        """Test Gmail API connection."""
        print("[Test] Testing Gmail API connection...")
        
        if not self.authenticate():
            return False
        
        try:
            # Get profile
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"[Test] Connected to: {profile['emailAddress']}")
            
            # Get unread count
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=1
            ).execute()
            
            unread_count = len(results.get('messages', []))
            print(f"[Test] Unread emails: {unread_count}+")
            
            print("[Test] Connection test PASSED")
            return True
            
        except Exception as e:
            print(f"[Test] Connection test FAILED: {e}")
            return False
    
    def show_status(self):
        """Show watcher status."""
        print("Gmail Watcher Status:")
        print(f"  Authenticated: {self.authenticated}")
        print(f"  Processed emails: {len(self.processed_ids)}")
        print(f"  Keywords: {', '.join(self.keywords)}")
        print(f"  VIP senders: {', '.join(self.vip_senders) if self.vip_senders else 'None'}")
        print(f"  Check interval: {self.check_interval}s")
        print(f"  Credentials: {self.credentials_path.exists()}")
        print(f"  Token: {self.token_path.exists()}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Gmail Watcher - Monitor Gmail for important emails',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gmail_watcher.py --auth     # First-time authentication
  python gmail_watcher.py --test     # Test connection
  python gmail_watcher.py            # Run continuously
  python gmail_watcher.py --once     # Run once (for scheduler)
        """
    )
    
    parser.add_argument('--vault', help='Vault path')
    parser.add_argument('--interval', type=int, default=120, help='Check interval (seconds)')
    parser.add_argument('--auth', action='store_true', help='Run authentication')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--clear-cache', action='store_true', help='Clear processed cache')
    
    args = parser.parse_args()
    
    watcher = GmailWatcher(args.vault, args.interval)
    
    if args.auth:
        print("Running authentication...")
        success = watcher.authenticate()
        sys.exit(0 if success else 1)
    
    elif args.test:
        success = watcher.test_connection()
        sys.exit(0 if success else 1)
    
    elif args.status:
        watcher.show_status()
        sys.exit(0)
    
    elif args.clear_cache:
        if watcher.processed_ids_file.exists():
            watcher.processed_ids_file.unlink()
            print("[Watcher] Cache cleared")
        else:
            print("[Watcher] No cache to clear")
        sys.exit(0)
    
    elif args.once:
        if not watcher.authenticate():
            sys.exit(1)
        count = watcher.run_once()
        print(f"[Watcher] Found {count} new email(s)")
        sys.exit(0)
    
    else:
        watcher.run()


if __name__ == '__main__':
    main()
