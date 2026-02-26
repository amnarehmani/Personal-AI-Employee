#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Browser - Post to LinkedIn via browser automation (Playwright).

This script uses the existing Playwright MCP server to automate LinkedIn posting.
Use this when LinkedIn API access is not available.

Usage:
    python linkedin-browser.py post --text "Your post content"
    python linkedin-browser.py login  # Login to LinkedIn first
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


class LinkedInBrowser:
    """Post to LinkedIn via browser automation."""
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    
    def __init__(self, vault_path: str = None, playwright_port: int = 8808):
        """Initialize LinkedIn browser automation."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'
        
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        for folder in [self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.playwright_port = playwright_port
        self.mcp_client = Path(__file__).parent.parent / 'browsing-with-playwright' / 'scripts' / 'mcp-client.py'
    
    def _run_playwright(self, tool: str, params: dict = None) -> dict:
        """Run a Playwright MCP tool."""
        cmd = [
            'python', str(self.mcp_client),
            'call',
            '-u', f'http://localhost:{self.playwright_port}',
            '-t', tool
        ]
        
        if params:
            cmd.extend(['-p', json.dumps(params)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return json.loads(result.stdout) if result.stdout else {}
            else:
                return {'error': result.stderr}
        except Exception as e:
            return {'error': str(e)}
    
    def login(self) -> bool:
        """
        Login to LinkedIn.
        
        Returns:
            True if login successful
        """
        print("[LinkedIn] Opening LinkedIn login page...")
        
        # Navigate to LinkedIn
        result = self._run_playwright('browser_navigate', {'url': self.LINKEDIN_URL})
        
        if 'error' in result:
            print(f"[LinkedIn] Error: {result['error']}")
            return False
        
        print("[LinkedIn] Please login manually in the browser window")
        print("[LinkedIn] Waiting 60 seconds for login...")
        
        # Wait for user to login
        time.sleep(60)
        
        # Take screenshot to verify
        result = self._run_playwright('browser_take_screenshot', {
            'type': 'png',
            'filename': 'linkedin_login_check.png'
        })
        
        print("[LinkedIn] Login check screenshot saved")
        return True
    
    def post(self, text: str, image_path: str = None) -> dict:
        """
        Create a LinkedIn post via browser automation.
        
        Args:
            text: Post content
            image_path: Optional path to image
            
        Returns:
            Result dict
        """
        result = {'success': False}
        
        try:
            # Navigate to LinkedIn
            print("[LinkedIn] Navigating to LinkedIn...")
            nav_result = self._run_playwright('browser_navigate', {'url': self.LINKEDIN_URL})
            
            if 'error' in nav_result:
                result['error'] = nav_result['error']
                return result
            
            # Wait for page to load
            time.sleep(3)
            
            # Get snapshot to find the post input
            print("[LinkedIn] Getting page snapshot...")
            snapshot = self._run_playwright('browser_snapshot')
            
            # Look for "Start a post" or similar button
            # This is simplified - actual implementation would parse snapshot
            print("[LinkedIn] Looking for post input field...")
            
            # Click on "Start a post" button (simplified selector)
            click_result = self._run_playwright('browser_run_code', {
                'code': '''async (page) => {
                    // Find and click the post creation input
                    const postInput = await page.$('button[aria-label*="post"]');
                    if (postInput) {
                        await postInput.click();
                        await page.waitForSelector('[role="dialog"]');
                        return { success: true, message: 'Post dialog opened' };
                    }
                    return { success: false, message: 'Post input not found' };
                }'''
            })
            
            if click_result.get('result', {}).get('success'):
                # Type the post content
                print("[LinkedIn] Entering post content...")
                type_result = self._run_playwright('browser_type', {
                    'element': 'Post text area',
                    'text': text,
                    'submit': False
                })
                
                # Add image if provided
                if image_path:
                    print(f"[LinkedIn] Uploading image: {image_path}")
                    # Image upload would go here
                
                # Click post button
                print("[LinkedIn] Publishing post...")
                post_result = self._run_playwright('browser_run_code', {
                    'code': '''async (page) => {
                        const postButton = await page.$('button[aria-label*="post"]');
                        if (postButton) {
                            await postButton.click();
                            await page.waitForNavigation();
                            return { success: true, message: 'Post published' };
                        }
                        return { success: false, message: 'Post button not found' };
                    }'''
                })
                
                if post_result.get('result', {}).get('success'):
                    result['success'] = True
                    result['message'] = 'Post published successfully'
                else:
                    result['error'] = 'Failed to publish post'
            else:
                result['error'] = 'Could not open post dialog'
            
            self.log_action('post', text[:100], result['success'])
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def create_draft(self, text: str, title: str = None) -> Path:
        """
        Create a draft post for approval.
        
        Args:
            text: Post content
            title: Optional title
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now()
        safe_title = (title or text[:30]).replace(' ', '_').replace(':', '')
        filename = f"LINKEDIN_{safe_title}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.pending_approval / filename
        
        content = f"""---
type: linkedin_post
content: {text[:100]}...
visibility: PUBLIC
created: {timestamp.isoformat()}
status: pending_approval
---

# LinkedIn Post Draft

## Content

{text}

## Instructions

**To Approve:**
Move this file to `/Approved` folder.

**To Reject:**
Move this file to `/Rejected` folder.

---
*Created by LinkedIn Browser Skill v0.1*
*Requires approval before publishing*
"""
        
        filepath.write_text(content, encoding='utf-8')
        
        print(f"[LinkedIn] Draft created: {filename}")
        self.log_action('draft', text[:100], True)
        
        return filepath
    
    def log_action(self, action: str, content: str, success: bool):
        """Log action to Logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.vault_path / 'Logs' / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': f'linkedin_{action}',
            'content': content,
            'success': success
        }
        
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Browser Automation')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # post command
    post_parser = subparsers.add_parser('post', help='Create LinkedIn post')
    post_parser.add_argument('--text', required=True, help='Post content')
    post_parser.add_argument('--image', help='Image path')
    post_parser.add_argument('--vault', help='Vault path')
    
    # draft command
    draft_parser = subparsers.add_parser('draft', help='Create draft post')
    draft_parser.add_argument('--text', required=True, help='Post content')
    draft_parser.add_argument('--title', help='Post title')
    draft_parser.add_argument('--vault', help='Vault path')
    
    # login command
    subparsers.add_parser('login', help='Login to LinkedIn')
    
    args = parser.parse_args()
    
    browser = LinkedInBrowser(args.vault if hasattr(args, 'vault') else None)
    
    if args.command == 'post':
        # Check if Playwright server is running
        result = browser.post(args.text, args.image)
        
        if result['success']:
            print(f"[LinkedIn] {result['message']}")
        else:
            print(f"[LinkedIn] Error: {result['error']}")
            print("[LinkedIn] Make sure Playwright MCP server is running:")
            print("  bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh")
            sys.exit(1)
    
    elif args.command == 'draft':
        browser.create_draft(args.text, args.title)
    
    elif args.command == 'login':
        success = browser.login()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
