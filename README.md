# OmniSight AI — OSINT Tool

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.1-orange)](https://github.com/AliZafar780/ai-osint-tool)
[![CodeQL](https://img.shields.io/badge/CodeQL-Passing-brightgreen)](https://github.com/AliZafar780/ai-osint-tool)

**OmniSight AI** is an advanced, modular Open-Source Intelligence (OSINT) tool with optional Groq-powered AI analysis. It performs comprehensive reconnaissance against domains and IP addresses through multiple intelligence-gathering modules.

---

## Features

| Module | Description |
|--------|-------------|
| **Basic Info** | IP geolocation, ISP/ASN data, domain registration details |
| **Subdomain Enumeration** | Brute‑force 30+ common subdomains with DNS resolution |
| **Port Scanning** | Multi‑threaded scan of 20+ common TCP ports |
| **Email Reconnaissance** | Regex‑based email address harvesting from web content |
| **Social Media Detection** | Generates search URLs across 6 major platforms |
| **Technology Stack Detection** | Identifies web servers, frameworks, and CMS platforms |
| **DNS Analysis** | Resolves A, NS, and MX records via dnspython |
| **URL Enumeration** | Probes 30+ common paths (robots.txt, .git/config, admin panels) |
| **Vulnerability Scanning** | Checks for exposed Git repos, .env files, phpinfo, and more |
| **Threat Intelligence** | Submits URLs to URLScan.io for reputation analysis |
| **WHOIS Lookup** | Queries domain registration data |
| **Groq AI Analysis** | AI‑powered security assessment via Llama 3 8B |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/AliZafar780/ai-osint-tool.git
cd ai-osint-tool

# Install dependencies
pip install -r requirements.txt

# (Optional) Run the setup script
chmod +x setup_osint.sh
./setup_osint.sh
```

### Dependencies

The following packages are required (see [requirements.txt](requirements.txt) for pinned versions):

- `requests` — HTTP client for API calls
- `colorama` — Cross‑platform colored terminal output
- `dnspython` — DNS record resolution
- `pyyaml` — YAML configuration parsing

---

## Usage

### Command Line

```bash
python3 advanced_osint_tool.py <target> [options]
```

**Positional arguments:**

| Argument | Description |
|----------|-------------|
| `target`  | Target domain (e.g., `example.com`) or IP address |

**Options:**

| Flag | Description |
|------|-------------|
| `-h, --help` | Show help message |
| `-o, --output FILE` | Save results to a file |
| `--ports PORTS` | Custom comma‑separated port list |
| `--groq-key KEY` | Groq API key for AI analysis |

### Examples

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

### GUI Interface

An optional Tkinter GUI is available:

```bash
python3 osint_gui.py
```

---

## Groq AI Integration

The Groq module uses the **Llama 3 8B** model to generate a security analysis report for the target, covering:

- Potential attack vectors
- Recommended security measures
- Common vulnerabilities to investigate
- Information‑gathering suggestions

**Setup:**

1. Obtain an API key from the [Groq Console](https://console.groq.com/keys)
2. Set it via environment variable:
   ```bash
   export GROQ_API_KEY="your_key_here"
   ```
3. Or pass it directly:
   ```bash
   python3 advanced_osint_tool.py example.com --groq-key "your_key_here"
   ```

> **Note:** If the API key is a placeholder value (e.g., `your_groq_api_key_here`), Groq analysis is automatically disabled.

---

## Configuration

Edit [`osint_config.yaml`](osint_config.yaml) to customise:

- Port scan target list
- Subdomain wordlist
- URL enumeration paths
- Vulnerability check paths
- Timeout and threading settings

---

## Project Structure

```
ai-osint-tool/
├── advanced_osint_tool.py   # Main OSINT engine (CLI)
├── osint_gui.py             # Optional Tkinter GUI
├── osint_config.yaml        # User configuration
├── requirements.txt         # Python dependencies
├── setup_osint.sh           # Virtual environment & permissions
├── run_osint.sh             # Quick‑run wrapper
├── SECURITY.md              # Security policy
├── LICENSE                  # MIT license
├── .gitignore
└── README.md                # This file
```

---

## Output

The tool provides:

- **Real‑time coloured console output** — blue for info, green for success, yellow for warnings, red for errors
- **Structured text report** — saved as `osint_report_<target>_<timestamp>.txt`

---

## Security Considerations

> This tool is intended for **authorised security research only**.

- Only scan targets you own or have explicit permission to test
- Respect `robots.txt` and website terms of service
- Be mindful of rate limits — aggressive scanning may trigger blocks
- Review local laws before use

---

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|-------------|----------|
| `ModuleNotFoundError` | Missing dependency | Run `pip install -r requirements.txt` |
| DNS resolution fails | Network / DNS config | Check connectivity and DNS servers |
| Connection timeouts | Firewall / rate limiting | Increase timeout in `osint_config.yaml` |
| Groq API returns 401 | Invalid API key | Verify key at [Groq Console](https://console.groq.com/keys) |
| Permission denied | File ownership | Use `chmod +x` on scripts |

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

## Author

**Ali Zafar** ([@AliZafar780](https://github.com/AliZafar780))

---

*OmniSight AI — See everything, know everything. Use responsibly.*
