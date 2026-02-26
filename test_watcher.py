#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the FileSystem Watcher works correctly.

Usage:
    python test_watcher.py

This script:
1. Creates a test file in the Inbox
2. Runs the watcher once to process it
3. Verifies the action file was created
4. Cleans up test files
"""

import os
import sys
import time
from pathlib import Path

# Add watchers directory to path
sys.path.insert(0, str(Path(__file__).parent / 'watchers'))

from filesystem_watcher import FileSystemWatcher


def test_filesystem_watcher():
    """Test the FileSystem Watcher functionality."""
    
    # Get vault path
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    
    if not vault_path.exists():
        print(f'[FAIL] Vault path does not exist: {vault_path}')
        print('  Run: mkdir -p AI_Employee_Vault/Inbox')
        return False
    
    print(f'[PASS] Vault path: {vault_path}')
    
    # Create watcher
    watcher = FileSystemWatcher(str(vault_path), check_interval=1)
    
    # Create test file
    inbox_path = vault_path / 'Inbox'
    inbox_path.mkdir(parents=True, exist_ok=True)
    
    test_file = inbox_path / 'test_watcher.txt'
    test_content = 'Test file for watcher verification\nTimestamp: ' + str(time.time())
    test_file.write_text(test_content)
    
    print(f'[PASS] Created test file: {test_file.name}')
    
    # Run check once (not the full loop)
    try:
        items = watcher.check_for_updates()
        
        if len(items) > 0:
            print(f'[PASS] Detected {len(items)} new file(s)')
            
            # Create action file
            for item in items:
                action_path = watcher.create_action_file(item)
                
                if action_path.exists():
                    print(f'[PASS] Created action file: {action_path.name}')
                    
                    # Verify action file content
                    content = action_path.read_text()
                    if 'type: file_drop' in content:
                        print(f'[PASS] Action file has correct format')
                    else:
                        print(f'[FAIL] Action file format incorrect')
                        return False
                else:
                    print(f'[FAIL] Failed to create action file')
                    return False
            
            print('\n[PASS] FileSystem Watcher test PASSED')
            
            # Cleanup
            test_file.unlink(missing_ok=True)
            print('  Cleaned up test file')
            
            return True
        else:
            print('[FAIL] No files detected - watcher may not be working')
            return False
            
    except Exception as e:
        print(f'[FAIL] Error during test: {e}')
        return False


def test_base_watcher_import():
    """Test that base_watcher can be imported."""
    try:
        from base_watcher import BaseWatcher
        print('[PASS] BaseWatcher imported successfully')
        return True
    except ImportError as e:
        print(f'[FAIL] Failed to import BaseWatcher: {e}')
        return False


def main():
    """Run all tests."""
    print('=' * 50)
    print('AI Employee - FileSystem Watcher Test')
    print('=' * 50)
    print()
    
    all_passed = True
    
    # Test 1: Import base watcher
    print('Test 1: Import BaseWatcher')
    if not test_base_watcher_import():
        all_passed = False
    print()
    
    # Test 2: Full watcher test
    print('Test 2: FileSystem Watcher End-to-End')
    if not test_filesystem_watcher():
        all_passed = False
    print()
    
    # Summary
    print('=' * 50)
    if all_passed:
        print('[PASS] ALL TESTS PASSED')
        print()
        print('Next steps:')
        print('1. Run watcher: python watchers/filesystem_watcher.py AI_Employee_Vault')
        print('2. Drop files in: AI_Employee_Vault/Inbox/')
        print('3. Check action files in: AI_Employee_Vault/Needs_Action/')
    else:
        print('[FAIL] SOME TESTS FAILED')
        print('  Check error messages above')
    print('=' * 50)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
