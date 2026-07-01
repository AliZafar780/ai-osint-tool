"""
Shodan/Censys Intelligence Module
Integration with Shodan and Censys for internet-wide device and service discovery.
"""

import requests
import time
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class ShodanIntel(OSINTModule):
    """Shodan and Censys integration for service/device intelligence."""

    name = "shodan_intel"
    description = "Shodan/Censys internet intelligence - exposed services, device info, vulnerabilities"
    requires_api_key = True
    api_key_name = "shodan_api_key"

    SHODAN_API = "https://api.shodan.io"
    CENSYS_API = "https://search.censys.io/api/v2"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OmniSightAI-ShodanIntel/2.0",
        })
        self.shodan_key = self._get_key("shodan_api_key")
        self.censys_id = self._get_key("censys_api_key")

    def _get_key(self, name: str) -> str:
        """Get API key from config or environment."""
        key = ""
        if self.config and "api_keys" in self.config:
            key = self.config["api_keys"].get(name, "")
        if not key:
            import os
            key = os.environ.get(name.upper(), "")
        return key.strip()

    def _shodan_host(self, ip: str) -> Dict:
        """Query Shodan for host information."""
        if not self.shodan_key:
            return {"error": "No Shodan API key configured. Set SHODAN_API_KEY env var."}

        try:
            resp = self.session.get(
                f"{self.SHODAN_API}/shodan/host/{ip}",
                params={"key": self.shodan_key},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "ip": data.get("ip_str", ip),
                    "org": data.get("org", "N/A"),
                    "os": data.get("os", "N/A"),
                    "ports": data.get("ports", []),
                    "hostnames": data.get("hostnames", []),
                    "country": data.get("country_name", "N/A"),
                    "city": data.get("city", "N/A"),
                    "vulns": list(data.get("vulns", {}).keys()),
                    "services": [
                        {
                            "port": s.get("port"),
                            "transport": s.get("transport", "tcp"),
                            "product": s.get("product", ""),
                            "version": s.get("version", ""),
                            "banner": (s.get("data", "") or "")[:200],
                        }
                        for s in data.get("data", [])
                    ],
                }
            elif resp.status_code == 403:
                return {"error": "Shodan API: Access denied (check key)"}
            else:
                return {"error": f"Shodan returned {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)[:100]}

    def _shodan_search(self, query: str) -> Dict:
        """Search Shodan for a query string."""
        if not self.shodan_key:
            return {"error": "No Shodan API key configured"}

        try:
            resp = self.session.get(
                f"{self.SHODAN_API}/shodan/host/search",
                params={"key": self.shodan_key, "query": query},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "total_results": data.get("total", 0),
                    "matches": [
                        {
                            "ip": m.get("ip_str"),
                            "port": m.get("port"),
                            "org": m.get("org", ""),
                            "hostnames": m.get("hostnames", []),
                            "country": m.get("location", {}).get("country_name", ""),
                        }
                        for m in data.get("matches", [])[:20]
                    ],
                }
            else:
                return {"error": f"Shodan search returned {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)[:100]}

    def _censys_search(self, query: str) -> Dict:
        """Search Censys for hosts matching a query."""
        if not self.censys_id:
            return {"error": "No Censys API key configured. Set CENSYS_API_KEY env var."}

        try:
            resp = self.session.get(
                f"{self.CENSYS_API}/hosts/search",
                params={"q": query, "per_page": 10},
                auth=(self.censys_id, ""),
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "total_results": data.get("result", {}).get("total", 0),
                    "hits": [
                        {
                            "ip": h.get("ip", ""),
                            "services": [
                                {
                                    "port": s.get("port"),
                                    "service_name": s.get("service_name", ""),
                                    "transport": s.get("transport_protocol", "tcp"),
                                }
                                for s in h.get("services", [])
                            ],
                            "location": h.get("location", {}),
                        }
                        for h in data.get("result", {}).get("hits", [])[:10]
                    ],
                }
            else:
                return {"error": f"Censys returned {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)[:100]}

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute Shodan/Censys intelligence.
        Target can be an IP address or a search query (e.g. 'apache', 'port:443').
        """
        start = time.time()

        results = {
            "target": target,
            "shodan_host": {},
            "shodan_search": {},
            "censys_search": {},
            "api_keys_configured": {
                "shodan": bool(self.shodan_key),
                "censys": bool(self.censys_id),
            },
        }

        import ipaddress
        import socket

        # Check if target is an IP
        is_ip = False
        try:
            ipaddress.ip_address(target)
            is_ip = True
        except ValueError:
            pass

        if is_ip:
            # Direct host lookup
            results["shodan_host"] = self._shodan_host(target)
            # Also search in Shodan
            results["shodan_search"] = self._shodan_search(f"hostname:/{target}/")
        else:
            # Try DNS resolution then host lookup
            try:
                ip = socket.gethostbyname(target)
                results["resolved_ip"] = ip
                results["shodan_host"] = self._shodan_host(ip)
            except Exception:
                results["resolution_error"] = "Could not resolve target"

            # Search both platforms
            results["shodan_search"] = self._shodan_search(f"hostname:{target}")
            results["censys_search"] = self._censys_search(target)

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
