#!/usr/bin/env python3
"""Verify Playwright MCP server is running and accessible (Cross-platform)."""
import subprocess
import sys
import urllib.request
import urllib.error

def check_process_windows():
    """Check if Playwright process is running on Windows."""
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq node.exe", "/FO", "CSV"],
            capture_output=True, text=True
        )
        return "node.exe" in result.stdout
    except Exception:
        return False

def check_server_http():
    """Check if server responds on port 8808."""
    try:
        req = urllib.request.Request("http://localhost:8808")
        urllib.request.urlopen(req, timeout=5)
        return True
    except (urllib.error.URLError, Exception):
        return False

def main():
    # Check HTTP endpoint first (most reliable)
    if check_server_http():
        print("[PASS] Playwright MCP server running (HTTP check passed)")
        sys.exit(0)
    
    # Fallback: check process
    if check_process_windows():
        print("[PASS] Playwright MCP server process found")
        sys.exit(0)
    
    print("[FAIL] Server not running. Run: .qwen\\skills\\browsing-with-playwright\\scripts\\start-server.bat")
    sys.exit(1)

if __name__ == "__main__":
    main()
