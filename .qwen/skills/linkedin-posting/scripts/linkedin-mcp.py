#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LinkedIn MCP - Post to LinkedIn via API or browser automation.

Usage:
    python linkedin-mcp.py post --text "Your post content"
    python linkedin-mcp.py draft --text "Draft content"
    python linkedin-mcp.py analytics --post-id "urn:li:share:xxx"
"""

import argparse
import json
import os
import sys
import requests
from pathlib import Path
from datetime import datetime


class LinkedInMCP:
    """Post to LinkedIn via API."""
    
    API_BASE = 'https://api.linkedin.com/v2'
    
    def __init__(self, vault_path: str = None):
        """Initialize LinkedIn MCP."""
        if vault_path:
            self.vault_path = Path(vault_path)
        else:
            self.vault_path = Path(__file__).parent.parent.parent / 'AI_Employee_Vault'
        
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        for folder in [self.pending_approval, self.approved, self.done]:
            folder.mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID', '')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET', '')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
        self.organization_id = os.getenv('LINKEDIN_ORGANIZATION_ID', '')
    
    def _get_headers(self) -> dict:
        """Get API request headers."""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
    
    def post(self, text: str, visibility: str = 'PUBLIC', 
             image_url: str = None, schedule_time: str = None) -> dict:
        """
        Create a LinkedIn post.
        
        Args:
            text: Post content
            visibility: PUBLIC, CONNECTIONS, or ANYONE
            image_url: Optional image URL
            schedule_time: Optional ISO 8601 timestamp for scheduling
            
        Returns:
            API response dict
        """
        if not self.access_token:
            return {
                'success': False,
                'error': 'LinkedIn access token not configured'
            }
        
        # Build post content
        post_content = {
            'author': f'urn:li:person:{self.client_id}',
            'lifecycleState': 'PUBLISHED',
            'specificContent': {
                'com.linkedin.ugc.ShareContent': {
                    'shareCommentary': {
                        'text': text
                    },
                    'shareMediaCategory': 'NONE'
                }
            },
            'visibility': {
                'com.linkedin.ugc.MemberNetworkVisibility': visibility
            }
        }
        
        # Add image if provided
        if image_url:
            post_content['specificContent']['com.linkedin.ugc.ShareContent']['shareMediaCategory'] = 'IMAGE'
        
        # Schedule if time provided
        if schedule_time:
            post_content['lifecycleState'] = 'SCHEDULED'
            post_content['scheduledPublishTime'] = schedule_time
        
        # Make API request
        try:
            response = requests.post(
                f'{self.API_BASE}/ugcPosts',
                headers=self._get_headers(),
                json=post_content
            )
            
            if response.status_code == 201:
                post_id = response.json().get('id', 'unknown')
                result = {
                    'success': True,
                    'post_id': post_id,
                    'message': f'Post created: {post_id}'
                }
            else:
                result = {
                    'success': False,
                    'error': f'API error: {response.status_code}',
                    'details': response.text
                }
            
            self.log_action('post', text[:100], result['success'])
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_draft(self, text: str, title: str = None, hashtags: list = None) -> Path:
        """
        Create a draft post for approval.
        
        Args:
            text: Post content
            title: Optional title
            hashtags: Optional list of hashtags
            
        Returns:
            Path to draft file
        """
        timestamp = datetime.now()
        safe_title = (title or text[:30]).replace(' ', '_').replace(':', '')
        filename = f"LINKEDIN_{safe_title}_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.pending_approval / filename
        
        # Add hashtags
        if hashtags:
            text += '\n\n' + ' '.join(f'#{tag}' for tag in hashtags)
        
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

## Hashtags
{', '.join(hashtags) if hashtags else 'None'}

## Visibility
Public

---

## Instructions

**To Approve:**
Move this file to `/Approved` folder.

**To Reject:**
Move this file to `/Rejected` folder.

---
*Created by LinkedIn Posting Skill v0.1*
*Requires approval before publishing*
"""
        
        filepath.write_text(content, encoding='utf-8')
        
        print(f"[LinkedIn] Draft created: {filename}")
        self.log_action('draft', text[:100], True)
        
        return filepath
    
    def get_analytics(self, post_id: str) -> dict:
        """
        Get post analytics.
        
        Args:
            post_id: LinkedIn post ID
            
        Returns:
            Analytics data
        """
        if not self.access_token:
            return {'error': 'Access token not configured'}
        
        try:
            # Note: LinkedIn analytics API requires special access
            # This is a placeholder for the actual implementation
            return {
                'post_id': post_id,
                'impressions': 'N/A (requires API access)',
                'engagement': 'N/A'
            }
        except Exception as e:
            return {'error': str(e)}
    
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
    parser = argparse.ArgumentParser(description='LinkedIn MCP')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # post command
    post_parser = subparsers.add_parser('post', help='Create LinkedIn post')
    post_parser.add_argument('--text', required=True, help='Post content')
    post_parser.add_argument('--visibility', default='PUBLIC', help='Visibility')
    post_parser.add_argument('--image', help='Image URL')
    post_parser.add_argument('--schedule', help='Schedule time (ISO 8601)')
    post_parser.add_argument('--vault', help='Vault path')
    
    # draft command
    draft_parser = subparsers.add_parser('draft', help='Create draft post')
    draft_parser.add_argument('--text', required=True, help='Post content')
    draft_parser.add_argument('--title', help='Post title')
    draft_parser.add_argument('--hashtags', help='Comma-separated hashtags')
    draft_parser.add_argument('--vault', help='Vault path')
    
    # analytics command
    analytics_parser = subparsers.add_parser('analytics', help='Get post analytics')
    analytics_parser.add_argument('--post-id', required=True, help='Post ID')
    analytics_parser.add_argument('--vault', help='Vault path')
    
    args = parser.parse_args()
    
    mcp = LinkedInMCP(args.vault if hasattr(args, 'vault') else None)
    
    if args.command == 'post':
        result = mcp.post(
            args.text,
            visibility=args.visibility,
            image_url=args.image,
            schedule_time=args.schedule
        )
        
        if result['success']:
            print(f"[LinkedIn] {result['message']}")
        else:
            print(f"[LinkedIn] Error: {result['error']}")
            sys.exit(1)
    
    elif args.command == 'draft':
        hashtags = [h.strip() for h in args.hashtags.split(',')] if args.hashtags else []
        mcp.create_draft(args.text, args.title, hashtags)
    
    elif args.command == 'analytics':
        analytics = mcp.get_analytics(args.post_id)
        print(f"Analytics for {args.post_id}:")
        print(json.dumps(analytics, indent=2))


if __name__ == '__main__':
    main()
