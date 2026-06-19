#!/bin/bash
set -e

echo "===================================================="
echo "NotebookLM MCP Server - One-Click Installer (Mac/Linux)"
echo "===================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 is not installed or not added to PATH."
    echo "Please install Python 3.10+ and try again."
    exit 1
fi

echo "[1/4] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[2/4] Installing dependencies..."
./venv/bin/python -m pip install --upgrade pip
./venv/bin/pip install -e .

echo "[3/4] Installing Playwright Chromium browser..."
./venv/bin/playwright install chromium

echo "[4/4] Configuring MCP Server for IDEs..."
./venv/bin/python install_mcp.py

echo ""
echo "===================================================="
echo "Installation Complete!"
echo "Please restart your IDE (Claude Desktop, Cursor, Antigravity)"
echo ""
echo "NOTE: Make sure you have authenticated NotebookLM by running:"
echo "./venv/bin/notebooklm login"
echo "===================================================="
