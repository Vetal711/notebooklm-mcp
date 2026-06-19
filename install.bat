@echo off
echo ====================================================
echo NotebookLM MCP Server - One-Click Installer (Windows)
echo ====================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo [2/4] Installing dependencies...
call venv\Scripts\pip install -e .

echo [3/4] Installing Playwright Chromium browser...
call venv\Scripts\playwright install chromium

echo [4/4] Configuring MCP Server for IDEs...
call venv\Scripts\python install_mcp.py

echo.
echo ====================================================
echo Installation Complete!
echo Please restart your IDE (Claude Desktop, Cursor, Antigravity)
echo.
echo NOTE: Make sure you have authenticated NotebookLM by running:
echo venv\Scripts\notebooklm.exe login
echo ====================================================
pause
