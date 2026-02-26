#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Notification Checker - Check LinkedIn notifications via Playwright.

Usage:
    python linkedin_notifications.py     # Check notifications
    python linkedin_notifications.py --post  # Create new post
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


class LinkedInNotificationChecker:
    """Check LinkedIn notifications via browser automation."""
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    
    def __init__(self, playwright_port: int = 8808):
        """Initialize notification checker."""
        self.playwright_port = playwright_port
        self.mcp_client = Path(__file__).parent.parent / '.qwen/skills/browsing-with-playwright/scripts/mcp-client.py'
        self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        self.logs = self.vault_path / 'Logs'
        self.logs.mkdir(parents=True, exist_ok=True)
    
    def _run_playwright(self, tool: str, params: dict = None) -> dict:
        """Run a Playwright MCP tool."""
        if not self.mcp_client.exists():
            return {'error': f'MCP client not found: {self.mcp_client}'}
        
        cmd = [
            'python', str(self.mcp_client),
            'call',
            '-u', f'http://localhost:{self.playwright_port}',
            '-t', tool
        ]
        
        if params:
            cmd.extend(['-p', json.dumps(params)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                return {'error': result.stderr or 'No output'}
        except subprocess.TimeoutExpired:
            return {'error': 'Command timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_notifications(self) -> dict:
        """
        Check LinkedIn notifications.
        
        Returns:
            Dict with notification data
        """
        result = {
            'success': False,
            'notifications': [],
            'error': None
        }
        
        try:
            # Navigate to LinkedIn notifications page
            print("[LinkedIn] Navigating to notifications...")
            nav_result = self._run_playwright('browser_navigate', {
                'url': f'{self.LINKEDIN_URL}/notifications/'
            })
            
            if 'error' in nav_result:
                result['error'] = nav_result['error']
                return result
            
            # Wait for page to load
            time.sleep(5)
            
            # Take screenshot
            print("[LinkedIn] Taking screenshot of notifications...")
            screenshot = self._run_playwright('browser_take_screenshot', {
                'type': 'png',
                'filename': f'linkedin_notifications_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            })
            
            if 'error' not in screenshot:
                result['success'] = True
                result['screenshot'] = screenshot.get('filename', 'saved')
                print(f"[LinkedIn] Screenshot saved: {result['screenshot']}")
            else:
                result['error'] = screenshot['error']
            
            # Get page content via snapshot
            print("[LinkedIn] Getting page content...")
            snapshot = self._run_playwright('browser_snapshot')
            
            if 'result' in snapshot:
                # Extract notification text from snapshot
                result['page_content'] = snapshot['result'].get('text', '')[:500]
            
            self.log_activity('check_notifications', result['success'])
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def create_post(self, content: str) -> dict:
        """
        Create a LinkedIn post.
        
        Args:
            content: Post content
            
        Returns:
            Result dict
        """
        result = {'success': False}
        
        try:
            # Navigate to LinkedIn
            print("[LinkedIn] Navigating to LinkedIn...")
            self._run_playwright('browser_navigate', {'url': self.LINKEDIN_URL})
            time.sleep(3)
            
            # Click "Start a post"
            print("[LinkedIn] Opening post dialog...")
            click_result = self._run_playwright('browser_run_code', {
                'code': '''async (page) => {
                    const buttons = await page.$$('button');
                    for (const button of buttons) {
                        const text = await page.evaluate(el => el.textContent, button);
                        if (text && text.toLowerCase().includes('start') && text.toLowerCase().includes('post')) {
                            await button.click();
                            await page.waitForTimeout(2000);
                            return { success: true };
                        }
                    }
                    return { success: false, message: 'Post button not found' };
                }'''
            })
            
            if click_result.get('result', {}).get('success'):
                # Type content
                print("[LinkedIn] Entering post content...")
                self._run_playwright('browser_type', {
                    'element': 'Post text area',
                    'text': content,
                    'submit': False
                })
                
                time.sleep(2)
                
                # Click post button
                print("[LinkedIn] Publishing...")
                post_result = self._run_playwright('browser_run_code', {
                    'code': '''async (page) => {
                        const buttons = await page.$$('button');
                        for (const button of buttons) {
                            const text = await page.evaluate(el => el.textContent, button);
                            if (text && text.toLowerCase().includes('post')) {
                                await button.click();
                                await page.waitForTimeout(3000);
                                return { success: true };
                            }
                        }
                        return { success: false };
                    }'''
                })
                
                result['success'] = post_result.get('result', {}).get('success', False)
            
            self.log_activity('create_post', result['success'])
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def log_activity(self, action: str, success: bool):
        """Log activity to Logs folder."""
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs / f'{today}.jsonl'
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event': f'linkedin_{action}',
            'success': success
        }
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception:
            pass


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Notification Checker')
    parser.add_argument('--post', action='store_true', help='Create new post')
    parser.add_argument('--content', help='Post content')
    parser.add_argument('--port', type=int, default=8808, help='Playwright port')
    
    args = parser.parse_args()
    
    checker = LinkedInNotificationChecker(args.port)
    
    if args.post:
        if not args.content:
            print("[Error] --content is required for posting")
            sys.exit(1)
        
        print("[LinkedIn] Creating post...")
        result = checker.create_post(args.content)
        
        if result['success']:
            print("[LinkedIn] Post published successfully!")
        else:
            print(f"[LinkedIn] Error: {result.get('error', 'Failed')}")
            sys.exit(1)
    
    else:
        print("[LinkedIn] Checking notifications...")
        result = checker.check_notifications()
        
        if result['success']:
            print(f"[LinkedIn] Notifications checked")
            print(f"[LinkedIn] Screenshot: {result.get('screenshot', 'N/A')}")
            if result.get('page_content'):
                print(f"\n[LinkedIn] Page content preview:")
                print(result['page_content'][:200])
        else:
            print(f"[LinkedIn] Error: {result.get('error', 'Failed')}")
            sys.exit(1)


if __name__ == '__main__':
    main()
