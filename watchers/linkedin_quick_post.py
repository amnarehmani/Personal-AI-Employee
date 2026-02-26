#!/usr/bin/env python3
"""
LinkedIn Quick Post - Simple helper to open LinkedIn and post.

Usage:
    python linkedin_quick_post.py
"""

import subprocess
import sys
import time
from pathlib import Path


def open_linkedin():
    """Open LinkedIn in the Playwright browser."""
    mcp_client = Path(__file__).parent.parent / '.qwen/skills/browsing-with-playwright/scripts/mcp-client.py'
    
    print("=" * 60)
    print("LinkedIn Quick Post Helper")
    print("=" * 60)
    print()
    print("Step 1: Opening LinkedIn...")
    
    # Navigate to LinkedIn
    cmd = [
        'python', str(mcp_client),
        'call',
        '-u', 'http://localhost:8808',
        '-t', 'browser_navigate',
        '-p', '{"url": "https://www.linkedin.com"}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ LinkedIn opened in browser!")
    else:
        print("✗ Error opening LinkedIn")
        print("Make sure Playwright server is running:")
        print("  npx @playwright/mcp@latest --port 8808")
        return False
    
    print()
    print("Step 2: Posting to LinkedIn")
    print("-" * 60)
    print()
    print("In the browser window, please:")
    print()
    print("  1. Click 'Start a post' button (usually at top of feed)")
    print("  2. Type or paste your post content")
    print("  3. Add images/videos if desired")
    print("  4. Click 'Post' button")
    print()
    print("-" * 60)
    print()
    
    # Wait and check
    print("Waiting 30 seconds for you to post...")
    time.sleep(30)
    
    print()
    print("Step 3: Taking screenshot to confirm")
    
    # Take screenshot
    cmd = [
        'python', str(mcp_client),
        'call',
        '-u', 'http://localhost:8808',
        '-t', 'browser_take_screenshot',
        '-p', '{"type": "png", "filename": "linkedin_post_confirm.png"}'
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Screenshot saved: linkedin_post_confirm.png")
    else:
        print("✗ Could not take screenshot")
    
    print()
    print("=" * 60)
    print("Done! Check the browser window to confirm your post.")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    open_linkedin()
