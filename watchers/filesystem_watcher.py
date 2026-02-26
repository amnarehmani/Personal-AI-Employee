#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File System Watcher - Monitors a drop folder for new files.

When files are added to the Inbox folder, this watcher:
1. Copies the file to Needs_Action
2. Creates a metadata .md file with file info
3. Claude Code can then process the action file

Usage:
    python filesystem_watcher.py /path/to/vault

For Bronze Tier: This is the recommended first watcher (simpler than Gmail).
"""

import os
import sys
import shutil
import hashlib
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """Watches a folder for new files and creates action files."""
    
    def __init__(self, vault_path: str, inbox_path: str = None, check_interval: int = 30):
        """
        Initialize the file system watcher.
        
        Args:
            vault_path: Path to the Obsidian vault root
            inbox_path: Path to the inbox/drop folder (default: vault/Inbox)
            check_interval: Seconds between checks (default: 30)
        """
        super().__init__(vault_path, check_interval)
        
        # Use Inbox folder inside vault if not specified
        if inbox_path:
            self.inbox_path = Path(inbox_path)
        else:
            self.inbox_path = self.vault_path / 'Inbox'
        
        # Ensure inbox exists
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        
        # Track processed files by hash
        self.processed_files = {}
    
    def _get_file_hash(self, filepath: Path) -> str:
        """Calculate MD5 hash of file to detect duplicates."""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f'Error hashing file {filepath}: {e}')
            return None
    
    def check_for_updates(self) -> list:
        """
        Check inbox folder for new files.
        
        Returns:
            list: List of new file paths to process
        """
        new_files = []
        
        try:
            for filepath in self.inbox_path.iterdir():
                if filepath.is_file() and not filepath.name.startswith('.'):
                    file_hash = self._get_file_hash(filepath)
                    
                    if file_hash and file_hash not in self.processed_files:
                        self.processed_files[file_hash] = filepath.name
                        new_files.append(filepath)
                        self.logger.info(f'New file detected: {filepath.name}')
        except Exception as e:
            self.logger.error(f'Error checking inbox: {e}')
        
        return new_files
    
    def create_action_file(self, filepath: Path) -> Path:
        """
        Create an action file for the dropped file.
        
        Args:
            filepath: Path to the new file
            
        Returns:
            Path: Path to the created action file
        """
        # Generate unique ID based on filename and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = filepath.name.replace(' ', '_').replace('.', '_')
        action_filename = f'FILE_DROP_{safe_name}_{timestamp}.md'
        action_path = self.needs_action / action_filename
        
        # Get file info
        try:
            stat = filepath.stat()
            file_size = stat.st_size
            file_type = filepath.suffix.lower()
        except Exception:
            file_size = 0
            file_type = 'unknown'
        
        # Create action file content
        content = f'''---
type: file_drop
source_file: {filepath.name}
file_type: {file_type}
file_size: {file_size} bytes
received: {datetime.now().isoformat()}
priority: normal
status: pending
---

# File Drop for Processing

## Source
- **Original File:** `{filepath.name}`
- **File Type:** {file_type}
- **Size:** {file_size} bytes
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Content Preview

*File content should be reviewed and processed*

## Suggested Actions

- [ ] Review file content
- [ ] Determine required action
- [ ] Process and move to /Done
- [ ] Archive original file

## Notes

*Add processing notes here*

---
*Created by FileSystem Watcher v0.1 for Qwen Code*
'''
        
        # Write action file
        action_path.write_text(content, encoding='utf-8')
        
        # Copy original file to vault for reference
        try:
            dest_path = self.vault_path / 'Inbox' / f'processed_{filepath.name}'
            shutil.copy2(filepath, dest_path)
            self.logger.info(f'Copied original file to: {dest_path}')
        except Exception as e:
            self.logger.warning(f'Could not copy original file: {e}')
        
        return action_path


def main():
    """Main entry point for running the watcher."""
    if len(sys.argv) < 2:
        # Default to vault in project directory
        vault_path = Path(__file__).parent / 'AI_Employee_Vault'
        print(f'No vault path specified, using default: {vault_path}')
    else:
        vault_path = Path(sys.argv[1])
    
    if not vault_path.exists():
        print(f'Error: Vault path does not exist: {vault_path}')
        sys.exit(1)
    
    watcher = FileSystemWatcher(str(vault_path), check_interval=30)
    watcher.run()


if __name__ == '__main__':
    main()
