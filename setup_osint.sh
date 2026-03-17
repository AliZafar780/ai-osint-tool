#!/bin/bash

# OSINT Tool Setup Script

echo "==================================="
echo "OSINT Tool Setup"
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

# Make scripts executable
echo "[*] Making scripts executable..."
chmod +x /home/aliz/advanced_osint_tool_v2.py

# Create output directory
echo "[*] Creating output directory..."
mkdir -p /home/aliz/osint_results

# Set environment variable prompt
echo ""
echo "[*] Setup complete!"
echo ""
echo "To use the tool:"
echo "  1. Activate virtual environment: source osint_venv/bin/activate"
echo "  2. Set Groq API key (optional): export GROQ_API_KEY='your_key'"
echo "  3. Run: python3 /home/aliz/advanced_osint_tool_v2.py <target>"
echo ""
echo "Example:"
echo "  python3 /home/aliz/advanced_osint_tool_v2.py example.com -o results.txt"
echo ""
