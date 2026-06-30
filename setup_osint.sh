#!/bin/bash

# OmniSight AI Setup Script

echo "==================================="
echo "OmniSight AI Setup"
echo "==================================="

# Create virtual environment
echo "[*] Creating virtual environment..."
python3 -m venv osint_venv

# Activate virtual environment
echo "[*] Activating virtual environment..."
source osint_venv/bin/activate

# Install dependencies
echo "[*] Installing dependencies..."
pip install --break-system-packages requests colorama dnspython pyyaml

# Determine script directory dynamically
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Make scripts executable
echo "[*] Making scripts executable..."
chmod +x "$SCRIPT_DIR/advanced_osint_tool.py"
chmod +x "$SCRIPT_DIR/osint_gui.py"

# Create output directory
echo "[*] Creating output directory..."
mkdir -p "$SCRIPT_DIR/osint_results"

# Set environment variable prompt
echo ""
echo "[*] Setup complete!"
echo ""
echo "To use the tool:"
echo "  1. Activate virtual environment: source osint_venv/bin/activate"
echo "  2. Set Groq API key (optional): export GROQ_API_KEY='your_key'"
echo "  3. Run: python3 \"$SCRIPT_DIR/advanced_osint_tool.py\" <target>"
echo ""
echo "Example:"
echo "  python3 \"$SCRIPT_DIR/advanced_osint_tool.py\" example.com -o results.txt"
echo ""
