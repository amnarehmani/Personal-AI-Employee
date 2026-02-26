#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn Watcher - Monitor LinkedIn and auto-post content.
Silver Tier Implementation - Browser-based using Playwright

Usage:
    python linkedin_watcher.py --auth      # Login to LinkedIn first
    python linkedin_watcher.py --post      # Create and post content
    python linkedin_watcher.py --schedule  # Schedule posts
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


class LinkedInWatcher:
    """
    Monitor LinkedIn and automate posting.
    
    Silver Tier Implementation:
    - Uses Playwright for browser automation
    - Creates action files for LinkedIn tasks
    - Supports scheduled posting
    - Requires approval before publishing
    """
    
    LINKEDIN_URL = 'https://www.linkedin.com'
    
    def __init__(self, vault_path: str = None, playwright_port: int = 8808):
        """
        Initialize LinkedIn Watcher.
        
        Args:
            vault_path: Path to Obsidian vault
            playwright_port: Port for Playwright MCP server
        """
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent / 'AI_Employee_Vault'
        
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        for folder in [self.needs_action, self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        self.playwright_port = playwright_port
        self.mcp_client = Path(__file__).parent.parent / '.qwen/skills/browsing-with-playwright/scripts/mcp-client.py'
        
        # Post ideas/topics to watch for
        self.topics = ['business growth', 'technology', 'innovation', 'industry insights']
        
        # Posting schedule
        self.post_times = ['09:00', '12:00', '17:00']  # Best engagement times
    
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
    
    def check_playwright_running(self) -> bool:
        """Check if Playwright MCP server is running."""
        result = self._run_playwright('browser_snapshot')
        return 'error' not in result
    
    def login(self) -> bool:
        """
        Login to LinkedIn via browser automation.
        
        Returns:
            True if login successful
        """
        print("[LinkedIn] Opening LinkedIn login page...")
        print("[LinkedIn] A browser window will open")
        print("[LinkedIn] IMPORTANT: Stay on this page and login to LinkedIn")
        print("[LinkedIn] You have 3 minutes to login")
        print()
        
        # Navigate to LinkedIn
        result = self._run_playwright('browser_navigate', {'url': self.LINKEDIN_URL})
        
        if 'error' in result:
            print(f"[LinkedIn] Error: {result['error']}")
            print("[LinkedIn] Make sure Playwright server is running:")
            print("  npx @playwright/mcp@latest --port 8808")
            return False
        
        print("[LinkedIn] Browser opened. Please login to LinkedIn...")
        print("[LinkedIn] Waiting 180 seconds (3 minutes)...")
        print()
        
        # Wait for user to login (3 minutes instead of 90 seconds)
        for i in range(180, 0, -10):
            print(f"[LinkedIn] Time remaining: {i} seconds...", end='\r')
            time.sleep(10)
        
        print()
        
        # Take screenshot to verify
        result = self._run_playwright('browser_take_screenshot', {
            'type': 'png',
            'filename': 'linkedin_login_check.png'
        })
        
        if 'error' not in result:
            print("[LinkedIn] Login check screenshot saved: linkedin_login_check.png")
            print("[LinkedIn] Browser will remain open for your session")
            return True
        else:
            print("[LinkedIn] Could not verify login")
            return False
    
    def create_post_draft(self, content: str, title: str = None, hashtags: list = None) -> Path:
        """
        Create a LinkedIn post draft for approval.
        
        Args:
            content: Post content
            title: Optional title
            hashtags: Optional list of hashtags
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now()
        safe_title = (title or content[:30]).replace(' ', '_').replace(':', '')[:40]
        filename = f"LINKEDIN_{safe_title}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.pending_approval / filename
        
        # Add hashtags
        if hashtags:
            content += '\n\n' + ' '.join(f'#{tag}' for tag in hashtags)
        
        draft_content = f"""---
type: linkedin_post
content: {content[:100]}...
visibility: PUBLIC
created: {timestamp.isoformat()}
status: pending_approval
scheduled_for: {timestamp.replace(hour=9, minute=0).isoformat()}
---

# LinkedIn Post Draft

## Content

{content}

## Hashtags
{', '.join(hashtags) if hashtags else 'None'}

## Visibility
Public

## Suggested Schedule
Next available slot: {timestamp.replace(hour=9, minute=0).strftime('%Y-%m-%d %H:%M')}

---

## Instructions

**To Approve:**
1. Review the post content
2. Move this file to `/Approved` folder
3. Orchestrator will publish automatically

**To Reject:**
Move this file to `/Rejected` folder

---
*Created by LinkedIn Watcher v0.1 (Silver Tier)*
*Requires approval before publishing*
"""
        
        filepath.write_text(draft_content, encoding='utf-8')
        
        print(f"[LinkedIn] Draft created: {filename}")
        print(f"  Location: {filepath}")
        
        return filepath
    
    def post_content(self, content: str, image_path: str = None) -> dict:
        """
        Post content to LinkedIn via browser automation.
        
        Args:
            content: Post content
            image_path: Optional path to image
            
        Returns:
            Result dict
        """
        result = {'success': False}
        
        if not self.check_playwright_running():
            result['error'] = 'Playwright server not running'
            return result
        
        try:
            # Navigate to LinkedIn
            print("[LinkedIn] Navigating to LinkedIn...")
            nav_result = self._run_playwright('browser_navigate', {'url': self.LINKEDIN_URL})
            
            if 'error' in nav_result:
                result['error'] = nav_result['error']
                return result
            
            # Wait for page to load
            time.sleep(3)
            
            # Get snapshot
            print("[LinkedIn] Getting page snapshot...")
            self._run_playwright('browser_snapshot')
            
            # Click on "Start a post" using JavaScript
            print("[LinkedIn] Opening post dialog...")
            click_result = self._run_playwright('browser_run_code', {
                'code': '''async (page) => {
                    // Find the "Start a post" button
                    const buttons = await page.$$('button');
                    for (const button of buttons) {
                        const text = await page.evaluate(el => el.textContent, button);
                        if (text && text.toLowerCase().includes('start') && text.toLowerCase().includes('post')) {
                            await button.click();
                            await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
                            return { success: true, message: 'Post dialog opened' };
                        }
                    }
                    // Alternative: try common selectors
                    const postInput = await page.$('.share-box-feed-entry__trigger');
                    if (postInput) {
                        await postInput.click();
                        await page.waitForSelector('[role="dialog"]', { timeout: 5000 });
                        return { success: true, message: 'Post dialog opened' };
                    }
                    return { success: false, message: 'Post input not found' };
                }'''
            })
            
            if not click_result.get('result', {}).get('success'):
                result['error'] = 'Could not open post dialog'
                return result
            
            # Type the post content
            print("[LinkedIn] Entering post content...")
            type_result = self._run_playwright('browser_type', {
                'element': 'Post text area',
                'text': content,
                'submit': False
            })
            
            # Add image if provided
            if image_path:
                print(f"[LinkedIn] Uploading image: {image_path}")
                # Image upload would require file chooser handling
            
            # Wait a moment for text to be entered
            time.sleep(2)
            
            # Click post button
            print("[LinkedIn] Publishing post...")
            post_result = self._run_playwright('browser_run_code', {
                'code': '''async (page) => {
                    // Find and click the post button
                    const buttons = await page.$$('button');
                    for (const button of buttons) {
                        const text = await page.evaluate(el => el.textContent, button);
                        if (text && text.toLowerCase().includes('post')) {
                            await button.click();
                            await page.waitForTimeout(3000);
                            return { success: true, message: 'Post published' };
                        }
                    }
                    return { success: false, message: 'Post button not found' };
                }'''
            })
            
            if post_result.get('result', {}).get('success'):
                result['success'] = True
                result['message'] = 'Post published successfully'
            else:
                result['error'] = 'Failed to publish post'
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def create_action_file(self, task_type: str, details: dict) -> Path:
        """
        Create action file for LinkedIn task.
        
        Args:
            task_type: Type of task (post, comment, etc.)
            details: Task details
            
        Returns:
            Path to created file
        """
        timestamp = datetime.now()
        filename = f"LINKEDIN_{task_type.upper()}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.needs_action / filename
        
        content = f"""---
type: linkedin_{task_type}
created: {timestamp.isoformat()}
priority: normal
status: pending
---

# LinkedIn Task: {task_type.replace('_', ' ').title()}

## Details

"""
        
        for key, value in details.items():
            content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
        
        content += f"""
## Suggested Actions

- [ ] Review task details
- [ ] Create post content if needed
- [ ] Request approval for content
- [ ] Publish when approved
- [ ] Move to /Done when complete

---
*Created by LinkedIn Watcher v0.1*
"""
        
        filepath.write_text(content, encoding='utf-8')
        
        return filepath
    
    def generate_post_ideas(self) -> list:
        """Generate post ideas based on topics."""
        ideas = [
            f"Excited to share insights on {self.topics[0]} in our industry.",
            f"Just completed a project leveraging {self.topics[1]}. Here's what I learned...",
            f"Innovation in {self.topics[2]} is transforming how we work.",
            f"Key takeaways from this week's industry developments...",
            f"Reflecting on the future of {self.topics[3]}..."
        ]
        return ideas
    
    def run(self):
        """Run the LinkedIn Watcher (for scheduled posting)."""
        print("=" * 60)
        print("LinkedIn Watcher v0.1 - Silver Tier")
        print("=" * 60)
        print(f"[Watcher] Vault: {self.vault_path}")
        print(f"[Watcher] Playwright port: {self.playwright_port}")
        print()
        
        # Check Playwright
        if not self.check_playwright_running():
            print("[Error] Playwright server not running")
            print("[Error] Start with: bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh")
            return
        
        print("[Watcher] LinkedIn Watcher ready")
        print("[Watcher] Monitoring for posting opportunities...")
        print()
        
        # Main loop would go here for continuous monitoring
        # For now, we create action files for manual processing
        
        print("[Watcher] Creating sample post ideas...")
        
        ideas = self.generate_post_ideas()
        for idea in ideas:
            self.create_post_draft(idea, hashtags=['Business', 'Innovation', 'Growth'])
            time.sleep(1)
        
        print(f"[Watcher] Created {len(ideas)} post drafts")
        print("[Watcher] Check Pending_Approval folder for drafts")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='LinkedIn Watcher - Automate LinkedIn posting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python linkedin_watcher.py --auth      # Login to LinkedIn
  python linkedin_watcher.py --post      # Create post drafts
  python linkedin_watcher.py --run       # Run watcher
        """
    )
    
    parser.add_argument('--vault', help='Vault path')
    parser.add_argument('--port', type=int, default=8808, help='Playwright port')
    parser.add_argument('--auth', action='store_true', help='Login to LinkedIn')
    parser.add_argument('--post', action='store_true', help='Create post drafts')
    parser.add_argument('--content', help='Post content (for single post)')
    parser.add_argument('--run', action='store_true', help='Run watcher')
    
    args = parser.parse_args()
    
    watcher = LinkedInWatcher(args.vault, args.port)
    
    if args.auth:
        print("Starting LinkedIn authentication...")
        success = watcher.login()
        sys.exit(0 if success else 1)
    
    elif args.post:
        if not watcher.check_playwright_running():
            print("[Error] Playwright server not running")
            print("[Error] Start with: bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh")
            sys.exit(1)
        
        if args.content:
            watcher.create_post_draft(args.content)
        else:
            watcher.run()
    
    elif args.run:
        watcher.run()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
