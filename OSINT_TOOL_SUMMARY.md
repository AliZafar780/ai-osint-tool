# Advanced OSINT Tool - Complete Package

## Files Created

### 1. Main Tool
- `advanced_osint_tool_v2.py` - Main OSINT tool with all modules

### 2. Supporting Files
- `osint_config.yaml` - Configuration file
- `setup_osint.sh` - Setup script
- `OSINT_TOOL_README.md` - Comprehensive documentation
- `osint_gui.py` - Optional GUI interface

### 3. Features Implemented

#### Core Modules
1. **Basic Information Gathering**
   - IP geolocation (ip-api.com)
   - WHOIS lookup (ipinfo.io)
   - Domain/IP details

2. **Subdomain Enumeration**
   - 30+ common subdomains
   - DNS resolution

3. **Port Scanning**
   - Multi-threaded (20 concurrent)
   - 20+ common ports

4. **Email Reconnaissance**
   - Regex pattern matching
   - Website scanning

5. **Social Media Detection**
   - Twitter, Facebook, LinkedIn
   - GitHub, Instagram, YouTube

6. **Technology Stack Detection**
   - Web server identification
   - Framework detection
   - CMS identification

7. **DNS Analysis**
   - A, NS, MX records
   - DNS resolution

8. **URL Enumeration**
   - 30+ common paths
   - Status code analysis

9. **Vulnerability Scanning**
   - Git repository exposure
   - Environment file detection
   - Common misconfigurations

10. **Threat Intelligence**
    - URLScan.io integration
    - Public API usage

11. **Groq AI Analysis**
    - Llama 3 8B model integration
    - Custom security prompts
    - Actionable recommendations

### 4. Usage Examples

#### Basic Scan
```bash
python3 advanced_osint_tool_v2.py example.com
```

#### With Output
```bash
python3 advanced_osint_tool_v2.py example.com -o results.txt
```

#### With Groq API
```bash
export GROQ_API_KEY="your_key"
python3 advanced_osint_tool_v2.py example.com
```

#### Custom Ports
```bash
python3 advanced_osint_tool_v2.py example.com --ports 80,443,8080
```

### 5. Installation

```bash
# Install dependencies
pip install --break-system-packages requests colorama dnspython

# Make executable
chmod +x advanced_osint_tool_v2.py

# Run setup script
./setup_osint.sh
```

### 6. Output

The tool generates:
- Real-time colored console output
- Comprehensive text report
- Timestamped results

### 7. Color Coding

- Blue: Informational
- Green: Success
- Yellow: Warning
- Red: Error
- Cyan: Data

### 8. Security Notes

⚠️ **For authorized security research only**

- Only scan targets you own
- Respect robots.txt
- Check local laws

### 9. Groq API Integration

The tool uses Groq's Llama 3 8B model for AI-powered security analysis. Features:

- Potential attack vectors
- Security recommendations
- Vulnerability assessment
- Information gathering suggestions

### 10. Configuration

Edit `osint_config.yaml` to customize:
- API keys
- Port scan options
- Subdomain list
- URL paths
- Vulnerability checks

### 11. GUI Interface

Optional GUI included in `osint_gui.py`:
- Tkinter-based interface
- Real-time output display
- Progress indication
- Easy configuration

### 12. Future Enhancements

- Proxy support
- More vulnerability checks
- Additional API integrations
- Database storage
- Scheduled scanning
- Multiple output formats

## Quick Start

1. Install dependencies:
   ```bash
   pip install --break-system-packages requests colorama dnspython
   ```

2. Run a scan:
   ```bash
   python3 advanced_osint_tool_v2.py example.com -o results.txt
   ```

3. For AI analysis, set Groq API key:
   ```bash
   export GROQ_API_KEY="your_api_key"
   python3 advanced_osint_tool_v2.py example.com
   ```

## Files Location

All files created in `/home/aliz/`:
- `advanced_osint_tool_v2.py` - Main tool
- `osint_config.yaml` - Configuration
- `setup_osint.sh` - Setup script
- `OSINT_TOOL_README.md` - Documentation
- `osint_gui.py` - GUI interface
- `OSINT_TOOL_SUMMARY.md` - This file

---
*Tool ready for use. Remember to use responsibly and legally.*
