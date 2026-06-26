#!/bin/bash
echo "===================================================="
echo "Starting interactive NotebookLM Login..."
echo "===================================================="
echo ""
echo "NOTE: If no browser window appears, DO NOT run this inside the AI agent console."
echo "Please open a standard OS terminal and run this script manually."
echo ""

cd "$(dirname "$0")" || exit
./venv/bin/notebooklm login
