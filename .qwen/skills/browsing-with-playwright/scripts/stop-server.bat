@echo off
REM Stop Playwright MCP Server - Windows Version

echo ===============================================
echo Playwright MCP Server - Stopping
echo ===============================================
echo.

REM Close browser via MCP client
python .qwen\skills\browsing-with-playwright\scripts\mcp-client.py call -u http://localhost:8808 -t browser_close -p {} 2>nul

REM Kill any remaining Playwright processes
echo [INFO] Stopping Playwright processes...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq Playwright*" 2>nul
taskkill /F /FI "IMAGENAME eq node.exe" /FI "CMDLINE eq *playwright*" 2>nul

echo [INFO] Server stopped
echo.
pause
