@echo off
REM Start Playwright MCP Server - Windows Version
REM Silver Tier - AI Employee

echo ===============================================
echo Playwright MCP Server - Starting
echo ===============================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found!
    echo Install from: https://nodejs.org/
    exit /b 1
)

echo [INFO] Node.js version:
node --version
echo.

REM Start Playwright MCP server (headed/visible by default)
echo [INFO] Starting Playwright MCP server on port 8808...
echo [INFO] A browser window will open for LinkedIn automation
echo [INFO] Press Ctrl+C to stop the server
echo.

REM Default is headed (visible browser). Use --headless for invisible.
npx @playwright/mcp@latest --port 8808 --shared-browser-context

pause
