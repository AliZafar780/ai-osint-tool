<div align="center">

# OmniSight AI

**Advanced Open-Source Intelligence (OSINT) Tool with Groq AI Integration**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.1-orange?style=flat-square)](https://github.com/AliZafar780/ai-osint-tool)
[![CodeQL](https://img.shields.io/badge/CodeQL-Passing-brightgreen?style=flat-square)](https://github.com/AliZafar780/ai-osint-tool)
[![AI](https://img.shields.io/badge/AI-Groq%20Llama%203-purple?style=flat-square)](#groq-ai-integration)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square)](#installation)
[![Dependencies](https://img.shields.io/badge/Dependencies-Minimal-blue?style=flat-square)](#dependencies)

`#osint` `#reconnaissance` `#threat-intelligence` `#ai` `#security-research`

</div>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Groq AI Integration](#groq-ai-integration)
- [Configuration](#configuration)
- [Output](#output)
- [GUI Interface](#gui-interface)
- [Project Structure](#project-structure)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**OmniSight AI** is a modular, multi-threaded Open-Source Intelligence (OSINT) tool that performs comprehensive reconnaissance against domains and IP addresses. It integrates **12 intelligence-gathering modules** covering DNS analysis, port scanning, subdomain enumeration, technology stack detection, vulnerability assessment, threat intelligence, and more.

The optional **Groq AI integration** (powered by Llama 3 8B) provides intelligent security analysis and recommendations based on collected intelligence.

### Key Capabilities

| Capability | Description |
|---|---|
| **12 Intelligence Modules** | DNS, ports, subdomains, emails, technology, vulnerabilities, threat intel, and more |
| **AI-Powered Analysis** | Groq Llama 3 8B for intelligent security assessment |
| **Multi-Threaded** | Concurrent scanning for rapid reconnaissance |
| **Real-Time Output** | Color-coded console output with progress tracking |
| **Structured Reports** | Timestamped text reports saved to disk |
| **GUI Interface** | Optional Tkinter-based graphical interface |
| **Fully Configurable** | YAML configuration for all scan parameters |
| **Minimal Dependencies** | Only 4 core Python packages required |

---

## Features

### Intelligence Modules

| Module | Description | Output |
|---|---|---|
| **Basic Information** | IP geolocation, ISP/ASN data, domain registration details | Location, organization, coordinates |
| **Subdomain Enumeration** | Brute-force 30+ common subdomains with DNS resolution | Resolved IP addresses for each subdomain |
| **Port Scanning** | Multi-threaded scan of 20+ common TCP ports | Open ports with service identification |
| **Email Reconnaissance** | Regex-based email address harvesting from web content | Extracted email addresses |
| **Social Media Detection** | Generates search URLs across 6 major platforms | Direct search URLs |
| **Technology Stack** | Identifies web servers, frameworks, and CMS platforms | Server headers, technology signatures |
| **DNS Analysis** | Resolves A, NS, MX, and TXT records via dnspython | Complete DNS record sets |
| **URL Enumeration** | Probes 30+ common paths (robots.txt, .git/config, admin panels) | HTTP status codes for each path |
| **Vulnerability Scanning** | Checks for exposed Git repos, .env files, phpinfo, and sensitive endpoints | Security findings with risk indicators |
| **Threat Intelligence** | Submits URLs to URLScan.io for reputation analysis | Scan ID, results URL, reputation data |
| **WHOIS Lookup** | Queries domain registration data | Registrar, dates, name servers |
| **Groq AI Analysis** | AI-powered security assessment via Llama 3 8B | Attack vectors, recommendations |

### Output Features

- **Color-coded console output**: Blue (info), Green (success), Yellow (warnings), Red (errors)
- **Structured text reports**: Automatically saved as `osint_report_<target>_<timestamp>.txt`
- **Real-time progress**: Each module reports completion status as scans execute
- **Summary statistics**: Total findings, open ports, vulnerabilities detected

---

## Installation

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/AliZafar780/ai-osint-tool.git
cd ai-osint-tool

# Install dependencies
pip install -r requirements.txt

# (Optional) Run setup script for virtual environment
chmod +x setup_osint.sh
./setup_osint.sh
```

### Dependencies

**Core (required):**

| Package | Version | Purpose |
|---|---|---|
| `requests` | >=2.28.0 | HTTP client for API calls |
| `colorama` | >=0.4.6 | Cross-platform colored terminal output |
| `dnspython` | >=2.3.0 | DNS record resolution |
| `pyyaml` | >=6.0 | YAML configuration parsing |

**Optional:**

| Package | Purpose |
|---|---|
| `groq` | Groq AI API client (for AI analysis) |

### Run Script

```bash
# Make executable
chmod +x run_osint.sh

# Quick run
./run_osint.sh example.com
```

---

## Usage

### Command Line Interface

```bash
python3 advanced_osint_tool.py <target> [options]
```

### Arguments

| Argument | Description | Required |
|---|---|---|
| `target` | Target domain (e.g., `example.com`) or IP address | Yes |

### Options

| Flag | Description | Default |
|---|---|---|
| `-h, --help` | Show help message and exit | — |
| `-o, --output FILE` | Save results to specified file | Auto-generated filename |
| `--ports PORTS` | Custom comma-separated port list | 20+ common ports |
| `--groq-key KEY` | Groq API key for AI analysis | `$GROQ_API_KEY` env var |

### Usage Examples

```bash
# Basic reconnaissance
python3 advanced_osint_tool.py example.com

# Save results to file
python3 advanced_osint_tool.py example.com -o results.txt

# Scan specific ports
python3 advanced_osint_tool.py example.com --ports 80,443,8080,8443

# With Groq AI analysis
export GROQ_API_KEY="your_api_key_here"
python3 advanced_osint_tool.py example.com

# Using the run script
./run_osint.sh example.com -o results.txt
```

### Example Output

```
[OmniSight AI] Starting reconnaissance on: example.com

[Basic Info]
  IP Address: 93.184.216.34
  ISP: Verizon Business
  Organization: ICANN
  City: Los Angeles
  Country: US

[Subdomains]
  www.example.com → 93.184.216.34
  mail.example.com → 93.184.216.35
  admin.example.com → 93.184.216.36

[Open Ports]
  80/tcp open (HTTP)
  443/tcp open (HTTPS)

[Vulnerabilities]
  [+] robots.txt found: /robots.txt
  [+] Security headers: Missing X-Frame-Options

[Threat Intelligence]
  URL submitted to URLScan.io
  Results: https://urlscan.io/result/abc123/

[Groq AI Analysis]
  Target: example.com
  Analysis: Medium risk profile detected.
  Recommendations: [1] Implement security headers (X-Frame-Options,
  Content-Security-Policy). [2] Regular vulnerability scanning recommended.

Report saved to: osint_report_example_com_20260101_120000.txt
```

---

## Groq AI Integration

The Groq module uses the **Llama 3 8B** model to generate a security analysis report for the target.

### Analysis Coverage

- Potential attack vectors and exploitation paths
- Recommended security hardening measures
- Common vulnerabilities to investigate further
- Information-gathering suggestions for deeper recon
- Overall risk assessment

### Setup

```bash
# Option 1: Environment variable
export GROQ_API_KEY="your_api_key_here"

# Option 2: Command-line argument
python3 advanced_osint_tool.py example.com --groq-key "your_api_key_here"
```

### Important Notes

- If the API key is a placeholder value (e.g., `your_groq_api_key_here`), Groq analysis is **automatically disabled**
- AI analysis requires internet connectivity
- All other modules function without AI — Groq is entirely optional

---

## Configuration

Edit [`osint_config.yaml`](osint_config.yaml) to customize scan parameters:

```yaml
# Port scan targets
ports:
  - 21    # FTP
  - 22    # SSH
  - 80    # HTTP
  - 443   # HTTPS
  - 8080  # HTTP-Proxy

# Subdomain wordlist
subdomains:
  - www
  - mail
  - admin
  - api
  - dev

# URL enumeration paths
url_paths:
  - /robots.txt
  - /.git/config
  - /admin
  - /.env
  - /wp-admin

# Threat intelligence
threat_intel:
  urlscan_enabled: true
  timeout: 30

# Performance
threading:
  max_workers: 10
  timeout: 10
```

### Configuration Options

| Section | Parameters | Description |
|---|---|---|
| `ports` | List of integers | TCP ports to scan |
| `subdomains` | List of strings | Subdomain wordlist for enumeration |
| `url_paths` | List of strings | URL paths to probe |
| `vuln_checks` | List of strings | Vulnerability check paths |
| `threat_intel` | Timeout, enabled | URLScan.io settings |
| `threading` | Max workers, timeout | Performance tuning |

---

## Output

### Console Output

The tool provides real-time, color-coded output:

| Color | Meaning |
|---|---|
| Blue | Informational messages and section headers |
| Green | Successful findings and positive results |
| Yellow | Warnings and items requiring attention |
| Red | Errors and critical security findings |

### Report Files

Reports are automatically saved with the naming convention:

```
osint_report_<target>_<YYYYMMDD>_<HHMMSS>.txt
```

Each report contains:
- Scan timestamp and target information
- Complete results from all modules
- Groq AI analysis (if enabled)
- Summary statistics

---

## GUI Interface

An optional Tkinter-based graphical interface is available:

```bash
python3 osint_gui.py
```

The GUI provides:
- Input field for target domain/IP
- Output file selection
- Run button with progress indication
- Scrollable output display
- Export functionality

---

## Project Structure

```
ai-osint-tool/
├── advanced_osint_tool.py   # Main OSINT engine (CLI)
├── osint_gui.py             # Optional Tkinter GUI
├── osint_config.yaml        # User configuration file
├── requirements.txt         # Python dependencies
├── setup_osint.sh           # Virtual environment & permissions setup
├── run_osint.sh             # Quick-run wrapper script
├── SECURITY.md              # Security policy and vulnerability reporting
├── LICENSE                  # MIT license
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## Security Considerations

> **This tool is intended for authorized security research and educational purposes only.**

### Responsible Use Guidelines

1. **Authorized Targets Only** — Only scan domains and IPs you own or have explicit written permission to test
2. **Respect robots.txt** — Honor website crawl policies and terms of service
3. **Rate Limiting** — Be mindful of request rates; aggressive scanning may trigger blocks or DOS protections
4. **Legal Compliance** — Review and comply with all applicable local, state, and international laws before use
5. **Data Handling** — Do not store or share collected intelligence irresponsibly

### Reporting Vulnerabilities

If you discover a security vulnerability in OmniSight AI, please report it responsibly via the process outlined in [SECURITY.md](SECURITY.md). **Do not** open public GitHub issues for security vulnerabilities.

---

## Troubleshooting

| Issue | Likely Cause | Solution |
|---|---|---|
| `ModuleNotFoundError` | Missing dependency | Run `pip install -r requirements.txt` |
| DNS resolution fails | Network / DNS configuration | Check connectivity and DNS server settings |
| Connection timeouts | Firewall / rate limiting | Increase timeout in `osint_config.yaml` |
| Groq API returns 401 | Invalid API key | Verify key at [Groq Console](https://console.groq.com/keys) |
| Permission denied | File ownership/permissions | Use `chmod +x` on shell scripts |
| Port scan slow | Too many ports or targets | Adjust `max_workers` in config |
| URLScan.io fails | Network / API limit | Check internet connectivity; wait before retry |
| No output file | Permission on output dir | Specify writable path with `-o` |

---

## Contributing

Contributions are welcome! Areas for contribution:

- Additional OSINT modules (e.g., Shodan, Censys, VirusTotal)
- Enhanced reporting formats (JSON, HTML, PDF)
- Performance optimizations
- Additional threat intelligence sources
- Documentation improvements

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full terms.

---

## Author

**Ali Zafar** ([@AliZafar780](https://github.com/AliZafar780))

---

<div align="center">
  <strong>OmniSight AI v2.0.1</strong><br>
  <sub>Advanced OSINT · AI-Powered Analysis · Modular · Multi-Threaded</sub>
  <br><br>
  <sub>See everything, know everything. Use responsibly.</sub>
</div>
