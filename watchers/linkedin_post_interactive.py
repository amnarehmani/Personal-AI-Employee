#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Interactive Poster - Open LinkedIn and post interactively.

Usage:
    python linkedin_post_interactive.py     # Interactive mode
    python linkedin_post_interactive.py --content "Your post"  # Direct post
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


class LinkedInInteractivePoster:
    """Post to LinkedIn interactively via browser."""
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    
    def __init__(self, playwright_port: int = 8808):
        """Initialize interactive poster."""
        self.playwright_port = playwright_port
        self.mcp_client = Path(__file__).parent.parent / '.qwen/skills/browsing-with-playwright/scripts/mcp-client.py'
        self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
    
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
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)
            else:
                return {'error': result.stderr or 'No output'}
        except subprocess.TimeoutExpired:
            return {'error': 'Command timed out'}
        except Exception as e:
            return {'error': str(e)}
    
    def open_linkedin(self):
        """Open LinkedIn in the browser."""
        print("[LinkedIn] Opening LinkedIn...")
        result = self._run_playwright('browser_navigate', {'url': self.LINKEDIN_URL})
        
        if 'error' in result:
            print(f"[Error] {result['error']}")
            return False
        
        print("[LinkedIn] LinkedIn opened in browser!")
        print("[LinkedIn] The browser window should now show LinkedIn homepage")
        time.sleep(2)
        return True
    
    def click_start_post(self):
        """Click the 'Start a post' button."""
        print("[LinkedIn] Looking for 'Start a post' button...")
        
        # Try to find and click the post button
        result = self._run_playwright('browser_run_code', {
            'code': '''async (page) => {
                try {
                    // Wait for page to load
                    await page.waitForTimeout(2000);
                    
                    // Try multiple selectors for "Start a post" button
                    const selectors = [
                        'button:has-text("Start a post")',
                        'button:has-text("Start")',
                        '.share-box-feed-entry__trigger',
                        '[aria-label*="post"]',
                        '[data-test-id*="post"]'
                    ];
                    
                    for (const selector of selectors) {
                        const button = await page.$(selector);
                        if (button) {
                            await button.click();
                            await page.waitForTimeout(2000);
                            return { success: true, message: 'Post dialog opened' };
                        }
                    }
                    
                    return { success: false, message: 'Post button not found' };
                } catch (e) {
                    return { success: false, message: e.message };
                }
            }'''
        })
        
        if result.get('result', {}).get('success'):
            print("[LinkedIn] Post dialog opened!")
            return True
        else:
            print(f"[LinkedIn] Could not open post dialog: {result.get('result', {}).get('message', 'Unknown error')}")
            return False
    
    def type_post_content(self, content: str):
        """Type the post content."""
        print(f"[LinkedIn] Typing post content ({len(content)} chars)...")
        
        result = self._run_playwright('browser_run_code', {
            'code': f'''async (page) => {{
                try {{
                    // Find the text editor in the post dialog
                    const editor = await page.$('.ProseMirror');
                    if (editor) {{
                        await editor.fill(`{content.replace('`', '\\`')}`);
                        await page.waitForTimeout(1000);
                        return {{ success: true, message: 'Content typed' }};
                    }}
                    
                    // Try alternative selector
                    const textarea = await page.$('textarea');
                    if (textarea) {{
                        await textarea.fill(`{content.replace('`', '\\`')}`);
                        await page.waitForTimeout(1000);
                        return {{ success: true, message: 'Content typed in textarea' }};
                    }}
                    
                    return {{ success: false, message: 'Editor not found' }};
                }} catch (e) {{
                    return {{ success: false, message: e.message }};
                }}
            }}'''
        })
        
        if result.get('result', {}).get('success'):
            print("[LinkedIn] Content typed successfully!")
            return True
        else:
            print(f"[LinkedIn] Could not type content: {result.get('result', {}).get('message', 'Unknown error')}")
            print("[LinkedIn] You can manually type the content in the browser")
            return False
    
    def take_screenshot(self, filename: str = 'linkedin_post_preview.png'):
        """Take a screenshot of the current page."""
        print(f"[LinkedIn] Taking screenshot: {filename}")
        
        result = self._run_playwright('browser_take_screenshot', {
            'type': 'png',
            'filename': filename,
            'fullPage': False
        })
        
        if 'error' not in result:
            print(f"[LinkedIn] Screenshot saved: {filename}")
            return True
        return False
    
    def post_interactive(self, content: str = None):
        """
        Interactive posting flow.
        
        Args:
            content: Optional post content to pre-fill
        """
        print("=" * 60)
        print("LinkedIn Interactive Poster")
        print("=" * 60)
        print()
        
        # Step 1: Open LinkedIn
        if not self.open_linkedin():
            return False
        
        print()
        print("[INFO] Please make sure you're logged into LinkedIn in the browser")
        print("[INFO] If not, please login now...")
        print()
        
        # Wait for user to be ready
        if not content:
            content = input("Enter your post content (or press Enter to skip): ").strip()
        
        if content:
            # Step 2: Click "Start a post"
            if self.click_start_post():
                # Step 3: Type content
                self.type_post_content(content)
                
                print()
                print("[LinkedIn] Post content is ready in the browser!")
                print("[LinkedIn] You can now:")
                print("  1. Add images/videos using the LinkedIn interface")
                print("  2. Add hashtags")
                print("  3. Tag people")
                print("  4. Click 'Post' button when ready")
                print()
                
                # Take screenshot
                self.take_screenshot()
                
                # Save a record
                self._save_post_record(content)
                
                return True
            else:
                print("[LinkedIn] Could not open post dialog automatically")
                print("[LinkedIn] Please click 'Start a post' manually in the browser")
        else:
            print("[LinkedIn] No content provided. LinkedIn is open in the browser.")
            print("[LinkedIn] You can manually create a post.")
        
        return True
    
    def _save_post_record(self, content: str):
        """Save a record of the post."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"LINKEDIN_POST_{timestamp}.md"
        filepath = self.vault_path / 'Done' / filename
        
        content_md = f"""---
type: linkedin_post
content: {content[:100]}...
created: {datetime.now().isoformat()}
status: posted
---

# LinkedIn Post

## Content
{content}

## Posted
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
*Posted via LinkedIn Interactive Poster*
"""
        
        try:
            filepath.write_text(content_md, encoding='utf-8')
            print(f"[LinkedIn] Post record saved: {filename}")
        except Exception as e:
            print(f"[Warning] Could not save post record: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='LinkedIn Interactive Poster')
    parser.add_argument('--content', help='Post content (optional)')
    parser.add_argument('--port', type=int, default=8808, help='Playwright port')
    
    args = parser.parse_args()
    
    poster = LinkedInInteractivePoster(args.port)
    
    if args.content:
        # Direct mode with content
        print(f"[LinkedIn] Posting: {args.content}")
        print()
        poster.post_interactive(args.content)
    else:
        # Interactive mode
        poster.post_interactive()


if __name__ == '__main__':
    main()
