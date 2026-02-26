#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the Orchestrator functionality.

Usage:
    python test_orchestrator.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import Orchestrator


def test_orchestrator_init():
    """Test orchestrator initialization."""
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    
    if not vault_path.exists():
        print("[FAIL] Vault path does not exist")
        return False
    
    print("[TEST] Initializing Orchestrator...")
    
    try:
        orchestrator = Orchestrator(str(vault_path), check_interval=5)
        print("[PASS] Orchestrator initialized successfully")
        print(f"  - Vault: {orchestrator.vault_path}")
        print(f"  - Qwen command: {orchestrator.qwen_command}")
        return True
    except Exception as e:
        print(f"[FAIL] Orchestrator initialization failed: {e}")
        return False


def test_check_for_tasks():
    """Test task detection."""
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    orchestrator = Orchestrator(str(vault_path), check_interval=5)
    
    # Create a test task
    needs_action = vault_path / 'Needs_Action'
    test_task = needs_action / 'TEST_ORCHESTRATOR.md'
    
    test_content = """---
type: test
status: pending
---

# Test Task

This is a test task for the orchestrator.
"""
    
    print(f"[TEST] Creating test task: {test_task.name}")
    test_task.write_text(test_content, encoding='utf-8')
    
    # Check if orchestrator detects it
    print("[TEST] Checking for new tasks...")
    tasks = orchestrator.check_for_new_tasks()
    
    # Clean up
    test_task.unlink(missing_ok=True)
    
    if len(tasks) > 0:
        print(f"[PASS] Detected {len(tasks)} task(s)")
        return True
    else:
        print("[FAIL] No tasks detected")
        return False


def test_build_prompt():
    """Test prompt building."""
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    orchestrator = Orchestrator(str(vault_path), check_interval=5)
    
    # Create mock task files
    task_files = [
        vault_path / 'Needs_Action' / 'test1.md',
        vault_path / 'Needs_Action' / 'test2.md'
    ]
    
    print("[TEST] Building Qwen prompt...")
    prompt = orchestrator.build_qwen_prompt(task_files)
    
    if prompt and 'AI Employee Task Processing' in prompt:
        print("[PASS] Prompt built successfully")
        print(f"  - Prompt length: {len(prompt)} chars")
        return True
    else:
        print("[FAIL] Prompt is empty or invalid")
        return False


def test_log_event():
    """Test event logging."""
    vault_path = Path(__file__).parent / 'AI_Employee_Vault'
    orchestrator = Orchestrator(str(vault_path), check_interval=5)
    
    print("[TEST] Logging test event...")
    orchestrator.log_event("test_event", {"test": "data", "count": 1})
    
    # Check if log file was created
    logs_folder = vault_path / 'Logs'
    today = time.strftime('%Y-%m-%d')
    log_file = logs_folder / f'{today}.jsonl'
    
    if log_file.exists():
        content = log_file.read_text(encoding='utf-8')
        if 'test_event' in content:
            print("[PASS] Event logged successfully")
            return True
    
    print("[FAIL] Event not logged")
    return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("AI Employee - Orchestrator Test Suite")
    print("=" * 60)
    print()
    
    all_passed = True
    
    # Test 1: Initialization
    print("Test 1: Orchestrator Initialization")
    if not test_orchestrator_init():
        all_passed = False
    print()
    
    # Test 2: Task Detection
    print("Test 2: Task Detection")
    if not test_check_for_tasks():
        all_passed = False
    print()
    
    # Test 3: Prompt Building
    print("Test 3: Prompt Building")
    if not test_build_prompt():
        all_passed = False
    print()
    
    # Test 4: Event Logging
    print("Test 4: Event Logging")
    if not test_log_event():
        all_passed = False
    print()
    
    # Summary
    print("=" * 60)
    if all_passed:
        print("[PASS] ALL TESTS PASSED")
        print()
        print("To run the orchestrator:")
        print("  python orchestrator.py AI_Employee_Vault")
    else:
        print("[FAIL] SOME TESTS FAILED")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
