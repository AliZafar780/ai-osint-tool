<div align="center">

# OmniSight AI v2.0

**Advanced Open-Source Intelligence (OSINT) Tool with Groq AI Integration**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-orange?style=flat-square)](https://github.com/AliZafar780/ai-osint-tool)
[![AI](https://img.shields.io/badge/AI-Groq%20Llama%203-purple?style=flat-square)](#ai-analysis)
[![Modules](https://img.shields.io/badge/Modules-20%2B-blueviolet?style=flat-square)](#intelligence-modules)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey?style=flat-square)](#installation)
[![Dashboard](https://img.shields.io/badge/Web%20Dashboard-FastAPI-green?style=flat-square)](#web-dashboard)

`#osint` `#reconnaissance` `#threat-intelligence` `#ai` `#security-research` `#dark-web` `#crypto-tracing`

</div>

---

## Table of Contents

- [Overview](#overview)
- [New in v2.0](#new-in-v20)
- [Intelligence Modules](#intelligence-modules)
- [Installation](#installation)
- [Usage](#usage)
- [AI Analysis](#ai-analysis)
- [Web Dashboard](#web-dashboard)
- [Report Generation](#report-generation)
- [Configuration](#configuration)
- [Output Caching](#output-caching)
- [Architecture](#architecture)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

**OmniSight AI v2.0** is a modular, **multi-threaded Open-Source Intelligence (OSINT) tool** that performs comprehensive reconnaissance against domains, IP addresses, email addresses, usernames, cryptocurrency addresses, and more. It integrates **20+ intelligence-gathering modules** covering:

| Category | Modules |
|---|---|
| **Web Recon** | DNS analysis, port scanning, subdomain enumeration, URL enumeration, tech stack fingerprinting |
| **Social Intelligence** | Social media profile discovery (20+ platforms), reverse image search, document metadata extraction |
| **Threat Intelligence** | Multi-source threat feeds (URLScan, VirusTotal, AlienVault), data breach checking, credential leak analysis |
| **Infrastructure** | Shodan/Censys integration, SSL/TLS certificate analysis, WHOIS lookups |
| **Advanced** | Dark web monitoring, cryptocurrency tracing, AI-powered Groq security analysis |
| **Output** | Multi-format reports (JSON, Markdown, HTML), web dashboard, real-time colored console output |

The optional **Groq AI integration** (powered by Llama 3 70B / Mixtral 8x7B) provides intelligent security analysis and actionable recommendations.

---

## New in v2.0

- **10 New OSINT Modules** — Social media intelligence, dark web monitoring, crypto tracing, breach intel, Shodan/Censys, reverse image, metadata extraction, threat intel feeds, SSL analysis, tech stack fingerprinting
- **Enhanced AI Integration** — Multi-model support (Llama 3 70B, Mixtral, Gemma), 5 analysis types (full, quick, vulnerability, remediation, compliance), context-aware prompts
- **Web Dashboard** — FastAPI-powered web interface for running scans and viewing results
- **Multi-Format Reports** — JSON (machine-parsable), Markdown (readable), HTML (styled with collapsible sections)
- **Output Caching** — In-memory and disk-based caching to avoid redundant lookups
- **Professional Package Structure** — Modular architecture with proper separation of concerns
- **Concurrent Execution** — Thread pool for parallel module execution with progress tracking

---

## Intelligence Modules

### Core Modules (Existing, Enhanced)

| Module | Description | Output |
|---|---|---|
| **Basic Information** | IP geolocation, ISP/ASN data, domain registration | Location, org, coordinates |
| **Subdomain Enumeration** | Brute-force 30+ common subdomains with DNS resolution | Resolved IPs for each subdomain |
| **Port Scanning** | Multi-threaded TCP port scan (20+ common ports) | Open ports with service detection |
| **Email Reconnaissance** | Regex-based email harvesting from web content | Extracted email addresses |
| **DNS Analysis** | A, NS, MX, TXT record resolution | Complete DNS record sets |
| **URL Enumeration** | Probes 30+ common paths (robots.txt, .git/config, admin) | HTTP status codes |
| **Vulnerability Scanning** | Checks for exposed Git repos, .env files, phpinfo | Security findings |
| **WHOIS Lookup** | Domain registration data query | Registrar, dates, name servers |

### New Modules (v2.0)

#### 1. Social Media Intelligence (`social_media`)
Discovers user profiles across **20+ social media platforms** including Twitter/X, LinkedIn, GitHub, Instagram, Reddit, YouTube, Medium, Dev.to, Twitch, TikTok, Pinterest, Telegram, Snapchat, and Facebook. Uses concurrent checking to verify profile existence.
- **Input:** Username, email, or domain
- **Output:** Found profiles with direct URLs, existence status per platform
- **Requires API key:** No

#### 2. Dark Web Monitoring (`dark_web`)
Monitors dark web sources for target mentions. Searches clearnet paste sites (Pastebin, Paste.ee, etc.), dark web search engines (Ahmia, OnionEngine), and performs simulated leak checks. Supports Tor `.onion` address extraction.
- **Input:** Domain, email, or username
- **Output:** Paste mentions, onion addresses, leak findings
- **Requires API key:** No (Tor/stem for advanced features)

#### 3. Cryptocurrency Tracing (`crypto_tracing`)
Blockchain forensics for Bitcoin and Ethereum addresses. Traces transactions, analyzes balances, and identifies transaction patterns. Detects crypto addresses in text content.
- **Input:** BTC address, ETH address, or text to scan for addresses
- **Output:** Transaction history, balance, risk indicators
- **Requires API key:** No (uses public blockchain APIs)

#### 4. Data Breach Intelligence (`breach_intel`)
Checks for compromised credentials across known data breaches. Uses k-anonymity model for password exposure checking (no plaintext transmission). Scans public paste dumps for target mentions.
- **Input:** Email address, username, or domain
- **Output:** Breach history, password exposures, public leak findings
- **Requires API key:** No (optional HIBP key for higher rate limits)

#### 5. Shodan/Censys Intelligence (`shodan_intel`)
Internet-wide device and service discovery. Queries Shodan for host details (open ports, services, vulnerabilities, organization) and Censys for additional asset discovery.
- **Input:** IP address or domain
- **Output:** Open ports, services, host info, vulns
- **Requires API key:** Yes (Shodan or Censys)

#### 6. Reverse Image Search (`reverse_image`)
Generates reverse image search links for Google Images, TinEye, Bing, and Yandex. Extracts EXIF metadata from image files using Pillow (GPS coordinates, camera info, timestamps).
- **Input:** Image URL or local file path
- **Output:** Search engine links, metadata, dimensions
- **Requires API key:** No

#### 7. Document Metadata Extraction (`metadata_extract`)
Extracts hidden metadata from PDFs, images, Office documents (DOCX/XLSX/PPTX), and other file types. Analyzes EXIF data, document properties, author information, and creation/modification dates.
- **Input:** File path or URL to download
- **Output:** File signatures, metadata fields, EXIF data
- **Requires API key:** No

#### 8. Threat Intelligence Feeds (`threat_intel`)
Aggregates data from multiple threat intelligence sources: URLScan.io, VirusTotal, and AlienVault OTX. Calculates a composite threat score and risk level.
- **Input:** Domain or IP address
- **Output:** Threat score, malicious indicators, IoC pulses
- **Requires API key:** Optional (for VirusTotal)

#### 9. SSL/TLS Certificate Analysis (`ssl_analysis`)
Full SSL/TLS security assessment: certificate chain analysis, protocol version support (TLS 1.0/1.1/1.2/1.3), security headers check (HSTS, CSP, X-Frame-Options), and security scoring with letter grade (A-F).
- **Input:** Domain or hostname:port
- **Output:** Certificate details, protocol support, security grade
- **Requires API key:** No

#### 10. Technology Stack Fingerprinting (`technology_stack`)
Advanced web technology detection with **100+ signatures** covering web servers, CMS platforms, JavaScript frameworks, CSS frameworks, analytics/tracking, CDNs, hosting providers, and programming languages.
- **Input:** URL or domain
- **Output:** Detected technologies by category, versions
- **Requires API key:** No

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

# Install core dependencies
pip install -r requirements.txt

# Install optional dependencies for full functionality
pip install fastapi uvicorn groq  # Dashboard + AI

# (Optional) Virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Dependencies

**Core (required):**
| Package | Version | Purpose |
|---|---|---|
| `requests` | >=2.28.0 | HTTP client |
| `colorama` | >=0.4.6 | Colored terminal output |
| `dnspython` | >=2.3.0 | DNS resolution |
| `pyyaml` | >=6.0 | Configuration parsing |
| `Pillow` | >=9.0.0 | Image metadata extraction |
| `cryptography` | >=41.0.0 | SSL certificate parsing |

**Optional:**
| Package | Purpose |
|---|---|
| `fastapi` + `uvicorn` | Web dashboard |
| `groq` | AI analysis client |
| `stem` | Tor controller for dark web |

---

## Usage

### Command Line Interface

```bash
python advanced_osint_tool.py <target> [options]
```

### Arguments

| Argument | Description | Required |
|---|---|---|
| `target` | Domain, IP, email, username, URL, or crypto address | Yes |

### Options

| Flag | Description | Default |
|---|---|---|
| `-m, --modules` | Comma-separated modules to run | All modules |
| `-f, --format` | Report formats: `json,markdown,html` | all three |
| `--groq-key KEY` | Groq API key for AI analysis | `$GROQ_API_KEY` |
| `--analysis-type` | AI analysis type: `full`, `quick`, `vulnerability`, `remediation`, `compliance` | `full` |
| `--dashboard` | Launch web dashboard | Off |
| `--dashboard-port` | Dashboard port number | 8080 |
| `--no-cache` | Disable output caching | Off |
| `-o, --output DIR` | Output directory | `./osint_results` |
| `-h, --help` | Show help | — |

### Usage Examples

```bash
# Full reconnaissance (all modules)
python advanced_osint_tool.py example.com

# Targeted modules
python advanced_osint_tool.py example.com -m social_media,threat_intel,ssl_analysis

# Specific report formats
python advanced_osint_tool.py example.com -f json,html

# With AI analysis
export GROQ_API_KEY="your_key_here"
python advanced_osint_tool.py example.com --analysis-type vulnerability

# Launch web dashboard
python advanced_osint_tool.py example.com --dashboard

# Email breach intelligence
python advanced_osint_tool.py user@example.com -m breach_intel

# Social media username check
python advanced_osint_tool.py @username -m social_media

# SSL analysis with custom port
python advanced_osint_tool.py example.com:8443 -m ssl_analysis

# Cryptocurrency tracing
python advanced_osint_tool.py 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa -m crypto_tracing
```

---

## AI Analysis

The Groq AI module provides intelligent security analysis using **Llama 3 70B**, **Mixtral 8x7B**, or **Gemma 2 9B**.

### Analysis Types

| Type | Description | Best For |
|---|---|---|
| `full` | Comprehensive security assessment with attack surface, vulns, recommendations | Deep dives |
| `quick` | Fast risk overview with top 3 concerns | Rapid triage |
| `vulnerability` | Focused CVE/exposure analysis | Bug hunting |
| `remediation` | Prioritized fix recommendations | Security hardening |
| `compliance` | Standards alignment (OWASP, NIST, ISO 27001) | Audits |

### Setup

```bash
# Via environment variable
export GROQ_API_KEY="your_key_here"
export GROQ_MODEL="llama3-70b-8192"  # or mixtral-8x7b-32768

# Via CLI argument
python advanced_osint_tool.py example.com --groq-key "your_key_here"
```

---

## Web Dashboard

The FastAPI-powered dashboard provides a browser interface for running scans:

```bash
# Launch with scan
python advanced_osint_tool.py example.com --dashboard

# Or start standalone
python -c "from dashboard.app import run_dashboard; run_dashboard()"
```

Open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.

**Dashboard features:**
- Target input and module selection
- Real-time scan progress with WebSocket-style polling
- Scan history with result viewing
- Multi-format report downloads
- REST API at `/api/` for programmatic access
- Mobile-responsive design

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard UI |
| `/api/health` | GET | System health |
| `/api/modules` | GET | List available modules |
| `/api/scan` | POST | Start new scan |
| `/api/scan/{id}` | GET | Get scan status |
| `/api/scan/{id}/report/{fmt}` | GET | Download report |
| `/api/history` | GET | Scan history |
| `/api/cache/stats` | GET | Cache statistics |

---

## Report Generation

Reports are automatically generated in your chosen formats:

### Output Formats

| Format | File Extension | Description |
|---|---|---|
| **JSON** | `.json` | Structured data for machine parsing and integration |
| **Markdown** | `.md` | Human-friendly with collapsible sections, tables, and formatting |
| **HTML** | `.html` | Professional styled report with collapsible modules, summary cards, and dark theme |

### Report Directory

Reports are saved to `./osint_results/` by default:

```
osint_results/
├── osint_report_example_com_20260701_120000.json
├── osint_report_example_com_20260701_120000.md
└── osint_report_example_com_20260701_120000.html
```

---

## Configuration

Edit [`osint_config.yaml`](osint_config.yaml) or set environment variables:

```yaml
api_keys:
  groq_api_key: ""          # or set GROQ_API_KEY env var
  shodan_api_key: ""        # or set SHODAN_API_KEY env var
  censys_api_key: ""        # or set CENSYS_API_KEY env var
  virustotal_api_key: ""    # or set VIRUSTOTAL_API_KEY env var

scan_options:
  timeout: 5                # Request timeout in seconds
  max_threads: 20           # Max concurrent threads
  user_agent: "Mozilla/5.0 ..."

cache:
  enabled: true
  ttl_seconds: 3600         # Cache TTL (1 hour)
  backend: "memory"         # memory or disk

dashboard:
  host: "127.0.0.1"
  port: 8080
  debug: false
```

Environment variables override config file values.

---

## Output Caching

OmniSight AI includes built-in caching to avoid redundant lookups:

- **Memory cache** (default): Fastest, cleared on restart
- **Disk cache**: Persistent across sessions, stored in `.cache/` directory
- **TTL**: Configurable time-to-live (default: 1 hour)
- Decorator-based: `@cached(key, ttl)` for easy module caching

Disable with `--no-cache` flag.

---

## Architecture

### Directory Structure

```
ai-osint-tool/
├── advanced_osint_tool.py    # CLI entry point (v2.0)
├── osint_gui.py              # Tkinter GUI (enhanced)
├── osint_config.yaml         # User configuration
├── requirements.txt          # Dependencies
├── setup.py                  # Pip installable package
├── SECURITY.md               # Security policy
├── LICENSE                   # MIT license
├── .gitignore                # Git ignore rules
├── README.md                 # This file
│
├── modules/                  # OSINT intelligence modules
│   ├── __init__.py           # Package exports
│   ├── base.py               # Base module class & ModuleResult
│   ├── social_media.py       # NEW: Social media intel
│   ├── dark_web.py           # NEW: Dark web monitoring
│   ├── crypto_tracing.py     # NEW: Crypto tracing
│   ├── breach_intel.py       # NEW: Breach intel
│   ├── shodan_intel.py       # NEW: Shodan/Censys
│   ├── reverse_image.py      # NEW: Reverse image search
│   ├── metadata_extract.py   # NEW: Metadata extraction
│   ├── threat_intel.py       # NEW: Threat intel feeds
│   ├── ssl_analysis.py       # NEW: SSL/TLS analysis
│   ├── technology_stack.py   # NEW: Tech stack fingerprinting
│   └── ai_analysis.py        # Enhanced: Groq AI analysis
│
├── reports/                  # Report generators
│   ├── __init__.py
│   ├── base_report.py        # Base report class
│   ├── json_report.py        # JSON reporter
│   ├── markdown_report.py    # Markdown reporter
│   └── html_report.py        # HTML reporter with CSS
│
├── dashboard/                # Web dashboard
│   ├── __init__.py
│   └── app.py                # FastAPI application
│
└── utils/                    # Utilities
    ├── __init__.py
    ├── config.py             # Configuration loader
    ├── cache.py              # Output caching (memory + disk)
    └── concurrent.py         # Thread pool & progress tracking
```

### Data Flow

```
User Input (CLI/Dashboard)
       │
       ▼
   OmniSightEngine ──► Config Loader ──► osint_config.yaml + env vars
       │
       ├──► Module 1 (Social Media) ──► ThreadPoolExecutor
       ├──► Module 2 (Dark Web)    ──► HTTP/API calls
       ├──► Module 3 (Crypto)      ──► Blockchain APIs
       ├──► ...
       └──► AI Analysis (Groq)     ──► Groq API
       │
       ▼
   ModuleResult (standardized)
       │
       ▼
   Report Generators ──► JSON + Markdown + HTML
       │
       ▼
   Output Files ──► osint_results/
```

---

## Security Considerations

> **This tool is intended for authorized security research and educational purposes only.**

### Responsible Use Guidelines

1. **Authorized Targets Only** — Only scan domains and IPs you own or have explicit written permission to test
2. **Respect robots.txt** — Honor website crawl policies and terms of service
3. **Rate Limiting** — Be mindful of request rates; aggressive scanning may trigger blocks
4. **Legal Compliance** — Review and comply with all applicable laws before use
5. **Data Handling** — Do not store or share collected intelligence irresponsibly

### API Key Security

- Never commit API keys to version control
- Use environment variables: `export GROQ_API_KEY="your_key"`
- The `.env` file is in `.gitignore`
- Revoke compromised keys immediately

### Reporting Vulnerabilities

See [SECURITY.md](SECURITY.md) for the responsible disclosure process.

---

## Troubleshooting

| Issue | Likely Cause | Solution |
|---|---|---|
| `ModuleNotFoundError` | Missing dependency | `pip install -r requirements.txt` |
| DNS resolution fails | Network / DNS config | Check connectivity and DNS settings |
| Connection timeouts | Firewall / rate limiting | Increase timeout in config |
| Groq API returns 401 | Invalid API key | Verify at [Groq Console](https://console.groq.com/keys) |
| Shodan API error | Missing/invalid key | Set `SHODAN_API_KEY` env var |
| Dashboard won't start | FastAPI not installed | `pip install fastapi uvicorn` |
| SSL analysis fails | No cryptography | `pip install cryptography` |
| Image metadata fails | No Pillow | `pip install Pillow` |
| Port scan slow | Too many ports | Reduce port list in config |
| Cache issues | Corrupted cache | `rm -rf .cache/` or use `--no-cache` |

---

## Contributing

Contributions are welcome! Areas for contribution:

- **Additional OSINT modules** (e.g., VirusTotal deep scan, DNS dumpster, social media APIs)
- **Enhanced reporting** (PDF via WeasyPrint, CSV export)
- **Performance optimizations** (async I/O, distributed scanning)
- **New data sources** (more threat feeds, blockchain explorers)
- **Documentation** (tutorials, video guides, use cases)

Please see [CONTRIBUTING](https://github.com/AliZafar780/ai-osint-tool/blob/main/CONTRIBUTING.md) guidelines.

---

## License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for full terms.

---

## Author

**Ali Zafar** ([@AliZafar780](https://github.com/AliZafar780))

---

<div align="center">
  <strong>OmniSight AI v2.0</strong><br>
  <sub>20+ OSINT Modules · AI-Powered Analysis · Web Dashboard · Multi-Format Reports</sub>
  <br><br>
  <sub>See everything, know everything. Use responsibly.</sub>
</div>
