# Advanced OSINT Tool with Groq AI Integration

## Overview

A comprehensive terminal-based OSINT (Open Source Intelligence) tool that gathers information about domains, IP addresses, and websites. Features Groq API integration for AI-powered security analysis.

## Features

### Core Modules

1. **Basic Information Gathering**
   - IP address geolocation
   - ISP/ASN information
   - WHOIS data
   - Domain registration details

2. **Subdomain Enumeration**
   - Common subdomain discovery
   - DNS resolution

3. **Port Scanning**
   - Multi-threaded port scanning
   - Common ports detection

4. **Email Reconnaissance**
   - Email harvesting from websites
   - Pattern matching

5. **Social Media Detection**
   - Search URLs for major platforms
   - Presence analysis

6. **Technology Stack Detection**
   - Web server identification
   - Framework detection
   - CMS identification

7. **DNS Analysis**
   - A, NS, MX records
   - DNS resolution

8. **URL Enumeration**
   - Common path discovery
   - Status code analysis

9. **Vulnerability Scanning**
   - Common misconfiguration checks
   - Exposure detection

10. **Threat Intelligence**
    - URL scanning integration
    - Reputation checks

11. **Groq AI Analysis**
    - AI-powered security analysis
    - Actionable recommendations

## Installation

```bash
# Install dependencies
pip install --break-system-packages requests colorama dnspython

# Make script executable
chmod +x advanced_osint_tool_v2.py
```

## Usage

### Basic Usage

```bash
python3 advanced_osint_tool_v2.py example.com
```

### With Output File

```bash
python3 advanced_osint_tool_v2.py example.com -o results.txt
```

### With Groq API Key

```bash
python3 advanced_osint_tool_v2.py example.com --groq-key your_api_key_here
```

### Set Groq API Key as Environment Variable

```bash
export GROQ_API_KEY="your_api_key_here"
python3 advanced_osint_tool_v2.py example.com
```

## Command-Line Options

```
positional arguments:
  target               Target domain or IP address

options:
  -h, --help           Show help message and exit
  -o, --output         Output file for results
  --ports              Custom ports (comma-separated)
  --groq-key           Groq API key
```

## Examples

### Scan a Domain

```bash
python3 advanced_osint_tool_v2.py google.com -o google_scan.txt
```

### Scan an IP Address

```bash
python3 advanced_osint_tool_v2.py 8.8.8.8 -o dns_scan.txt
```

### Custom Port Scan

```bash
python3 advanced_osint_tool_v2.py example.com --ports 80,443,8080,8443
```

### With AI Analysis

```bash
export GROQ_API_KEY="your_groq_api_key"
python3 advanced_osint_tool_v2.py example.com
```

## Output

The tool generates:
- Real-time console output with color coding
- Comprehensive text report saved to file
- Timestamped results for each module

## Color Coding

- **Blue**: Informational messages
- **Green**: Success messages
- **Yellow**: Warning messages
- **Red**: Error messages
- **Cyan**: Data output

## Groq API Integration

The tool uses Groq's Llama 3 8B model for AI-powered security analysis. To use this feature:

1. Get a Groq API key from [Groq Console](https://console.groq.com/keys)
2. Set it as environment variable or pass via command line
3. The AI will analyze the target and provide:
   - Potential attack vectors
   - Security recommendations
   - Vulnerability assessment
   - Information gathering suggestions

## Security Considerations

⚠️ **WARNING**: This tool is for authorized security research only. 

- Only scan targets you own or have explicit permission to test
- Respect robots.txt and terms of service
- Be mindful of rate limiting
- Check local laws and regulations

## Modules Details

### Basic Info Module
- Uses ip-api.com for IP geolocation
- Retrieves WHOIS information via ipinfo.io
- Extracts domain registration details

### Subdomain Module
- Tests common subdomain patterns
- Uses DNS resolution for verification

### Port Scan Module
- Multi-threaded scanning (20 concurrent connections)
- 1-second timeout per port
- Common port list customizable

### Email Recon Module
- Regex pattern matching for email addresses
- Duplicates removal
- Website content scanning

### Technology Stack Module
- HTTP header analysis
- Content pattern detection
- Framework identification

### DNS Module
- A, NS, MX record resolution
- Uses dnspython library

### URL Enumeration Module
- Common paths discovery
- HTTP HEAD requests for efficiency
- Status code analysis

### Vulnerability Scan Module
- Git repository exposure
- Environment file detection
- Common misconfigurations

### Threat Intelligence Module
- URLScan.io integration
- Public API usage

### Groq AI Analysis Module
- Llama 3 8B model
- Custom security-focused prompts
- Detailed recommendations

## Troubleshooting

### Common Issues

1. **DNS Resolution Errors**
   - Check network connectivity
   - Verify DNS server configuration

2. **Connection Timeouts**
   - Increase timeout values
   - Check firewall settings

3. **Groq API Errors**
   - Verify API key validity
   - Check rate limits
   - Ensure proper authentication

4. **Permission Errors**
   - Run with appropriate privileges
   - Check file permissions for output

## Future Enhancements

- Proxy support
- More advanced vulnerability scanning
- Integration with additional APIs
- GUI interface option
- Database storage for results
- Scheduled scanning
- Report generation in multiple formats (HTML, PDF)

## License

This tool is provided for educational and authorized security research purposes only.

## Author

Security Researcher
Version 2.0

---
*Remember: Always obtain proper authorization before scanning any target.*
