"""
Configuration loader for OmniSight AI.
Loads settings from YAML config file, environment variables, and CLI args.
"""

import os
import yaml
from typing import Any, Dict, Optional


DEFAULT_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "osint_config.yaml",
)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file, merging with environment variables."""
    config = {
        "api_keys": {},
        "scan_options": {
            "timeout": 5,
            "max_threads": 20,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
        "port_scan": {
            "common_ports": [
                21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143,
                443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080,
            ]
        },
        "subdomains": {
            "common_list": [
                "www", "mail", "ftp", "admin", "test", "dev", "staging",
                "api", "blog", "shop", "portal", "web", "m", "mobile",
                "app", "apps", "cpanel", "whm", "webmail", "ns1", "ns2",
                "smtp", "pop", "pop3", "imap", "owa", "vpn", "remote",
            ]
        },
        "urls": {
            "common_paths": [
                "/robots.txt", "/sitemap.xml", "/.git/config", "/.env",
                "/composer.json", "/wp-admin", "/wp-login.php",
                "/admin", "/login", "/api", "/upload", "/uploads",
            ]
        },
        "vulnerability_checks": [
            "/.git/config", "/.env", "/phpinfo.php",
            "/server-status", "/wp-admin", "/composer.json",
        ],
        "output": {
            "format": "text",
            "directory": "./osint_results",
            "timestamp": True,
        },
        "cache": {
            "enabled": True,
            "ttl_seconds": 3600,
            "backend": "memory",
        },
        "dashboard": {
            "host": "127.0.0.1",
            "port": 8080,
            "debug": False,
        },
    }

    # Load from file
    path = config_path or DEFAULT_CONFIG_PATH
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                file_config = yaml.safe_load(f)
            if file_config:
                _deep_merge(config, file_config)
        except Exception as e:
            logger.warning(f"Failed to load config file {path}: {e}")
    else:
        logger.info(f"No config file at {path}, using defaults")

    # Environment variables override
    env_groq = os.environ.get("GROQ_API_KEY", "").strip()
    if env_groq:
        config["api_keys"]["groq_api_key"] = env_groq

    env_shodan = os.environ.get("SHODAN_API_KEY", "").strip()
    if env_shodan:
        config["api_keys"]["shodan_api_key"] = env_shodan

    env_censys = os.environ.get("CENSYS_API_KEY", "").strip()
    if env_censys:
        config["api_keys"]["censys_api_key"] = env_censys

    env_virustotal = os.environ.get("VIRUSTOTAL_API_KEY", "").strip()
    if env_virustotal:
        config["api_keys"]["virustotal_api_key"] = env_virustotal

    return config


def _deep_merge(base: Dict, override: Dict) -> None:
    """Deep merge override dict into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value


import logging

logger = logging.getLogger("omnisight.config")
