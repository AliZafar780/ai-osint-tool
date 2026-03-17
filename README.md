# OmniSight AI - OSINT Tool

![OmniSight AI](https://img.shields.io/badge/OmniSight-AI-blue)
![Python](https://img.shields.io/badge/Python-3.7%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Version](https://img.shields.io/badge/Version-2.0-orange)
![Groq](https://img.shields.io/badge/Groq-AI-purple)

**OmniSight AI** - Advanced AI-Powered OSINT Tool with Groq API Integration for comprehensive security intelligence gathering.

## 🌟 Features

### 🔍 Core Intelligence Modules

1. **Basic Information Gathering** - IP geolocation, WHOIS data, domain details
2. **Subdomain Enumeration** - 30+ common subdomains with DNS resolution
3. **Port Scanning** - Multi-threaded scanning of 20+ common ports
4. **Email Reconnaissance** - Pattern matching for email addresses
5. **Social Media Detection** - Search URLs for major platforms
6. **Technology Stack Detection** - Web server, framework, CMS identification
7. **DNS Analysis** - A, NS, MX records resolution
8. **URL Enumeration** - 30+ common paths with status codes
9. **Vulnerability Scanning** - Common misconfiguration checks
10. **Threat Intelligence** - URLScan.io integration
11. **Groq AI Analysis** - AI-powered security analysis using Llama 3 8B

### ✨ Key Features

- **Multi-threaded operations** for lightning-fast scanning
- **Color-coded output** for easy reading
- **Comprehensive reporting** with timestamps
- **Groq AI integration** for intelligent analysis
- **Configurable** via YAML file
- **Optional GUI** interface
- **Modular design** for easy extension
- **Real-time AI insights** powered by Groq

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/AliZafar780/ai-osint-tool.git
cd ai-osint-tool

# Install dependencies
pip install requests colorama dnspython

# Or use setup script
chmod +x setup_osint.sh
./setup_osint.sh
```

### Basic Usage

```bash
# Basic scan
python3 advanced_osint_tool_v2.py example.com

# With output file
python3 advanced_osint_tool_v2.py example.com -o results.txt

# With Groq API key (AI analysis)
export GROQ_API_KEY="your_api_key_here"
python3 advanced_osint_tool_v2.py example.com

# Custom ports
python3 advanced_osint_tool_v2.py example.com --ports 80,443,8080,8443

# Using quick run script
./run_osint.sh example.com -o results.txt

# GUI Interface
python3 osint_gui.py
```

## 📊 Command-Line Options

```
positional arguments:
  target               Target domain or IP address

options:
  -h, --help           Show help message and exit
  -o, --output         Output file for results
  --ports              Custom ports (comma-separated)
  --groq-key           Groq API key
```

## 🎯 Examples

### Scan a Domain
```bash
python3 advanced_osint_tool_v2.py google.com -o google_scan.txt
```

### Scan an IP Address
```bash
python3 advanced_osint_tool_v2.py 8.8.8.8 -o dns_scan.txt
```

### With AI Analysis
```bash
export GROQ_API_KEY="your_groq_api_key"
python3 advanced_osint_tool_v2.py example.com
```

## 📁 Project Structure

```
omnisight-ai/
├── advanced_osint_tool_v2.py  # Main OSINT tool
├── osint_config.yaml          # Configuration file
├── setup_osint.sh            # Setup script
├── run_osint.sh              # Quick run script
├── osint_gui.py              # GUI interface
├── README.md                 # This file
├── LICENSE                   # MIT License
└── .gitignore               # Git ignore file
```

## 🎨 Output Features

### Color Coding
- **Blue**: Informational messages
- **Green**: Success messages
- **Yellow**: Warning messages
- **Red**: Error messages
- **Cyan**: Data output

### Report Generation
- Real-time console output with colors
- Comprehensive text report saved to file
- Timestamped results for each module

## 🔮 Groq AI Integration

**OmniSight AI** uses Groq's Llama 3 8B model for AI-powered security analysis:

1. Get a Groq API key from [Groq Console](https://console.groq.com/keys)
2. Set it as environment variable or pass via command line
3. The AI will analyze the target and provide:
   - Potential attack vectors
   - Security recommendations
   - Vulnerability assessment
   - Information gathering suggestions

## ⚙️ Configuration

Edit `osint_config.yaml` to customize:
- API keys
- Port scan options
- Subdomain list
- URL paths
- Vulnerability checks

## ⚠️ Security Considerations

**WARNING**: This tool is for authorized security research only.

- Only scan targets you own or have explicit permission to test
- Respect robots.txt and terms of service
- Be mindful of rate limiting
- Check local laws and regulations

## 🐛 Troubleshooting

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

## 🚧 Future Enhancements

- [ ] Proxy support
- [ ] More advanced vulnerability scanning
- [ ] Integration with additional APIs
- [ ] Database storage for results
- [ ] Scheduled scanning
- [ ] Report generation in multiple formats (HTML, PDF)
- [ ] More AI models integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Ali Zafar (alizafarbati)**
- GitHub: [@AliZafar780](https://github.com/AliZafar780)
- Email: alizafarbati@gmail.com

## 🙏 Acknowledgments

- Groq for providing the AI API
- ip-api.com for IP geolocation
- ipinfo.io for WHOIS data
- URLScan.io for threat intelligence

## 📢 Disclaimer

This tool is provided for educational and authorized security research purposes only. The author assumes no liability for any misuse or damage caused by this tool. Always obtain proper authorization before scanning any target.

---
**OmniSight AI** - See everything, know everything. 
*Remember: Always obtain proper authorization before scanning any target.*
