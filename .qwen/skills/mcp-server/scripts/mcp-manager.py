#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP Manager - Manage all MCP servers from one place.

Usage:
    python mcp-manager.py start-all       # Start all servers
    python mcp-manager.py start <server>  # Start specific server
    python mcp-manager.py stop <server>   # Stop specific server
    python mcp-manager.py status          # Check all server status
    python mcp-manager.py health <server> # Health check
"""

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime


class MCPManager:
    """Manage MCP servers."""
    
    DEFAULT_CONFIG = {
        'servers': {
            'browser': {
                'enabled': True,
                'port': 8808,
                'command': 'npx',
                'args': ['@playwright/mcp@latest', '--port', '{port}', '--shared-browser-context'],
                'health_check': 'http://localhost:{port}'
            },
            'email': {
                'enabled': True,
                'port': 8809,
                'command': 'python',
                'args': ['.qwen/skills/email-mcp/scripts/email-server.py', '--serve', '--port', '{port}'],
                'health_check': None  # Custom health check
            },
            'linkedin': {
                'enabled': False,
                'port': 8810,
                'command': 'python',
                'args': ['.qwen/skills/linkedin-posting/scripts/linkedin-mcp.py', '--serve', '--port', '{port}'],
                'health_check': None
            },
            'approval': {
                'enabled': True,
                'port': 8811,
                'command': 'python',
                'args': ['.qwen/skills/approval-workflow/scripts/approval-manager.py', '--serve', '--port', '{port}'],
                'health_check': None
            }
        },
        'pid_dir': '.mcp_pids'
    }
    
    def __init__(self, project_root: str = None):
        """Initialize MCP manager."""
        if project_root:
            self.project_root = Path(project_root)
        else:
            self.project_root = Path(__file__).parent.parent.parent
        
        self.config_file = self.project_root / '.mcp_config.json'
        self.pid_dir = self.project_root / '.mcp_pids'
        self.logs_dir = self.project_root / 'Logs' / 'mcp'
        
        # Load or create config
        self.config = self._load_config()
        
        # Ensure directories exist
        self.pid_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()
    
    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _get_pid_file(self, server_name: str) -> Path:
        """Get PID file path for server."""
        return self.pid_dir / f'{server_name}.pid'
    
    def _get_log_file(self, server_name: str) -> Path:
        """Get log file path for server."""
        return self.logs_dir / f'{server_name}.log'
    
    def _is_running(self, pid: int) -> bool:
        """Check if process is running."""
        try:
            os.kill(pid, 0)
            return True
        except (OSError, ProcessLookupError):
            return False
    
    def _get_pid(self, server_name: str) -> int:
        """Get PID for server."""
        pid_file = self._get_pid_file(server_name)
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    return int(f.read().strip())
            except (ValueError, IOError):
                pass
        return None
    
    def start_server(self, server_name: str) -> bool:
        """
        Start an MCP server.
        
        Args:
            server_name: Name of server to start
            
        Returns:
            True if started successfully
        """
        if server_name not in self.config['servers']:
            print(f"[MCP] Unknown server: {server_name}")
            print(f"Available servers: {', '.join(self.config['servers'].keys())}")
            return False
        
        server_config = self.config['servers'][server_name]
        
        if not server_config.get('enabled', True):
            print(f"[MCP] Server {server_name} is disabled in config")
            return False
        
        # Check if already running
        existing_pid = self._get_pid(server_name)
        if existing_pid and self._is_running(existing_pid):
            print(f"[MCP] {server_name} already running (PID: {existing_pid})")
            return True
        
        # Build command
        port = server_config.get('port', 8808)
        cmd = [server_config['command']]
        
        args = [arg.replace('{port}', str(port)) for arg in server_config['args']]
        cmd.extend(args)
        
        print(f"[MCP] Starting {server_name} on port {port}...")
        print(f"[MCP] Command: {' '.join(cmd)}")
        
        # Start process
        log_file = self._get_log_file(server_name)
        
        try:
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    cmd,
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    cwd=str(self.project_root),
                    start_new_session=True
                )
            
            # Save PID
            pid_file = self._get_pid_file(server_name)
            with open(pid_file, 'w') as f:
                f.write(str(process.pid))
            
            # Wait for server to start
            time.sleep(2)
            
            # Check if still running
            if self._is_running(process.pid):
                print(f"[MCP] {server_name} started (PID: {process.pid})")
                return True
            else:
                print(f"[MCP] {server_name} failed to start. Check logs: {log_file}")
                return False
                
        except Exception as e:
            print(f"[MCP] Error starting {server_name}: {e}")
            return False
    
    def stop_server(self, server_name: str) -> bool:
        """
        Stop an MCP server.
        
        Args:
            server_name: Name of server to stop
            
        Returns:
            True if stopped successfully
        """
        pid = self._get_pid(server_name)
        
        if not pid:
            print(f"[MCP] {server_name} is not running (no PID file)")
            return True
        
        if not self._is_running(pid):
            print(f"[MCP] {server_name} is not running (PID {pid} not found)")
            self._get_pid_file(server_name).unlink(missing_ok=True)
            return True
        
        print(f"[MCP] Stopping {server_name} (PID: {pid})...")
        
        try:
            # Try graceful shutdown
            os.kill(pid, signal.SIGTERM)
            
            # Wait for process to stop
            for _ in range(10):
                time.sleep(1)
                if not self._is_running(pid):
                    print(f"[MCP] {server_name} stopped")
                    self._get_pid_file(server_name).unlink(missing_ok=True)
                    return True
            
            # Force kill if still running
            print(f"[MCP] Force killing {server_name}...")
            os.kill(pid, signal.SIGKILL)
            self._get_pid_file(server_name).unlink(missing_ok=True)
            return True
            
        except Exception as e:
            print(f"[MCP] Error stopping {server_name}: {e}")
            return False
    
    def start_all(self) -> dict:
        """
        Start all enabled servers.
        
        Returns:
            Dict of server names to success status
        """
        results = {}
        
        for server_name, config in self.config['servers'].items():
            if config.get('enabled', True):
                results[server_name] = self.start_server(server_name)
            else:
                results[server_name] = 'disabled'
        
        return results
    
    def stop_all(self) -> dict:
        """
        Stop all servers.
        
        Returns:
            Dict of server names to success status
        """
        results = {}
        
        for server_name in self.config['servers'].keys():
            results[server_name] = self.stop_server(server_name)
        
        return results
    
    def status(self) -> list:
        """
        Get status of all servers.
        
        Returns:
            List of server status dicts
        """
        statuses = []
        
        for server_name, config in self.config['servers'].items():
            pid = self._get_pid(server_name)
            running = pid and self._is_running(pid)
            
            statuses.append({
                'name': server_name,
                'enabled': config.get('enabled', True),
                'port': config.get('port'),
                'running': running,
                'pid': pid if running else None
            })
        
        return statuses
    
    def health_check(self, server_name: str) -> dict:
        """
        Perform health check on server.
        
        Args:
            server_name: Name of server to check
            
        Returns:
            Health status dict
        """
        config = self.config['servers'].get(server_name)
        
        if not config:
            return {'error': f'Unknown server: {server_name}'}
        
        pid = self._get_pid(server_name)
        running = pid and self._is_running(pid)
        
        if not running:
            return {'status': 'not_running', 'healthy': False}
        
        # Check health endpoint if configured
        health_url = config.get('health_check')
        if health_url:
            try:
                import requests
                health_url = health_url.replace('{port}', str(config.get('port', 8808)))
                response = requests.get(health_url, timeout=5)
                
                if response.status_code == 200:
                    return {'status': 'healthy', 'healthy': True, 'pid': pid}
                else:
                    return {'status': 'unhealthy', 'healthy': False, 'pid': pid}
                    
            except Exception as e:
                return {'status': f'health_check_failed: {e}', 'healthy': False, 'pid': pid}
        
        # No health endpoint, just check if running
        return {'status': 'running', 'healthy': True, 'pid': pid}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='MCP Server Manager')
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # start command
    start_parser = subparsers.add_parser('start', help='Start server')
    start_parser.add_argument('server', help='Server name')
    
    # stop command
    stop_parser = subparsers.add_parser('stop', help='Stop server')
    stop_parser.add_argument('server', help='Server name')
    
    # restart command
    restart_parser = subparsers.add_parser('restart', help='Restart server')
    restart_parser.add_argument('server', help='Server name')
    
    # start-all command
    subparsers.add_parser('start-all', help='Start all servers')
    
    # stop-all command
    subparsers.add_parser('stop-all', help='Stop all servers')
    
    # status command
    subparsers.add_parser('status', help='Show server status')
    
    # health command
    health_parser = subparsers.add_parser('health', help='Health check')
    health_parser.add_argument('server', help='Server name')
    
    args = parser.parse_args()
    
    manager = MCPManager()
    
    if args.command == 'start':
        success = manager.start_server(args.server)
        sys.exit(0 if success else 1)
    
    elif args.command == 'stop':
        success = manager.stop_server(args.server)
        sys.exit(0 if success else 1)
    
    elif args.command == 'restart':
        manager.stop_server(args.server)
        time.sleep(1)
        success = manager.start_server(args.server)
        sys.exit(0 if success else 1)
    
    elif args.command == 'start-all':
        results = manager.start_all()
        print("\n[MCP] Server Status:")
        for name, status in results.items():
            symbol = '✓' if status else '✗'
            print(f"  {symbol} {name}: {status}")
    
    elif args.command == 'stop-all':
        results = manager.stop_all()
        print("\n[MCP] All servers stopped")
    
    elif args.command == 'status':
        statuses = manager.status()
        
        print("\nMCP Server Status:")
        print("=" * 50)
        
        for s in statuses:
            status_icon = '✓' if s['running'] else '✗'
            enabled_icon = 'E' if s['enabled'] else 'D'
            
            print(f"\n  {s['name']}:")
            print(f"    Status: {status_icon} {'Running' if s['running'] else 'Stopped'}")
            print(f"    Enabled: {enabled_icon}")
            print(f"    Port: {s['port']}")
            if s['running'] and s['pid']:
                print(f"    PID: {s['pid']}")
    
    elif args.command == 'health':
        result = manager.health_check(args.server)
        print(f"\nHealth Check: {args.server}")
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
