#!/bin/bash
# Quick run script for OSINT tool

if [ $# -eq 0 ]; then
    echo "Usage: $0 <target> [options]"
    echo "Example: $0 example.com -o results.txt"
    echo ""
    echo "Options:"
    echo "  -o <file>    Output file"
    echo "  --groq-key <key>  Groq API key"
    echo "  --ports <ports>   Custom ports (comma-separated)"
    exit 1
fi

TARGET=$1
shift

python3 /home/aliz/advanced_osint_tool_v2.py "$TARGET" "$@"
