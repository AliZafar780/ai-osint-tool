"""
Threat Intelligence Feeds Module
Aggregates data from multiple threat intelligence sources and feeds.
"""

import requests
import time
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .base import OSINTModule, ModuleResult


class ThreatIntel(OSINTModule):
    """Aggregated threat intelligence - feeds, reputation, IoCs, malware analysis."""

    name = "threat_intel"
    description = "Multi-source threat intelligence - reputation, malware analysis, IoC collection"

    # Threat intelligence feed sources
    FEEDS = {
        "urlscan": {
            "url": "https://urlscan.io/api/v1/search/?q={target}",
            "type": "domain",
        },
        "virustotal": {
            "url": "https://www.virustotal.com/api/v3/domains/{target}",
            "type": "domain",
            "needs_key": True,
        },
        "alienvault_otx": {
            "url": "https://otx.alienvault.com/api/v1/indicators/domain/{target}/general",
            "type": "domain",
            "needs_key": False,
        },
        "abuseipdb": {
            "url": "https://api.abuseipdb.com/api/v2/check",
            "type": "ip",
            "needs_key": True,
        },
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OmniSightAI-ThreatIntel/2.0",
        })
        self.api_keys = {}
        if config and "api_keys" in config:
            self.api_keys = config["api_keys"]

    def _urlscan_lookup(self, target: str) -> Dict:
        """Query URLScan.io for domain intelligence."""
        result = {"source": "URLScan.io", "found": False, "data": {}}

        try:
            resp = self.session.get(
                f"https://urlscan.io/api/v1/search/?q={target}",
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                if results:
                    result["found"] = True
                    result["data"]["total_results"] = data.get("total", 0)
                    result["data"]["scans"] = [
                        {
                            "url": r.get("page", {}).get("url", ""),
                            "ip": r.get("page", {}).get("ip", ""),
                            "domain": r.get("page", {}).get("domain", ""),
                            "server": r.get("page", {}).get("server", ""),
                            "verdict": r.get("verdict", {}).get("overall", {}).get("malicious", False),
                            "country": r.get("page", {}).get("country", ""),
                            "scan_date": r.get("task", {}).get("time", ""),
                        }
                        for r in results[:10]
                    ]
                    result["data"]["malicious_scans"] = sum(
                        1 for s in result["data"]["scans"] if s["verdict"]
                    )
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def _virustotal_lookup(self, target: str) -> Dict:
        """Query VirusTotal for domain reputation."""
        result = {"source": "VirusTotal", "found": False, "data": {}}
        vt_key = self.api_keys.get("virustotal_api_key", "")

        if not vt_key:
            result["error"] = "No VirusTotal API key configured"
            return result

        try:
            resp = self.session.get(
                f"https://www.virustotal.com/api/v3/domains/{target}",
                headers={"x-apikey": vt_key},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                attrs = data.get("data", {}).get("attributes", {})
                result["found"] = True
                result["data"]["reputation"] = attrs.get("reputation", 0)
                result["data"]["last_analysis_stats"] = attrs.get("last_analysis_stats", {})
                result["data"]["categories"] = attrs.get("categories", {})
                result["data"]["total_votes"] = attrs.get("total_votes", {})
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def _alienvault_lookup(self, target: str) -> Dict:
        """Query AlienVault OTX for domain intelligence."""
        result = {"source": "AlienVault OTX", "found": False, "data": {}}

        try:
            resp = self.session.get(
                f"https://otx.alienvault.com/api/v1/indicators/domain/{target}/general",
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                result["found"] = True
                result["data"]["pulse_count"] = data.get("pulse_info", {}).get("count", 0)
                result["data"]["pulses"] = [
                    {
                        "name": p.get("name", ""),
                        "description": (p.get("description", "") or "")[:200],
                        "tags": p.get("tags", []),
                        "created": p.get("created", ""),
                        "adversary": p.get("adversary", ""),
                    }
                    for p in data.get("pulse_info", {}).get("pulses", [])[:10]
                ]
                result["data"]["validation"] = data.get("validation", [])
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def _alienvault_ip_lookup(self, target: str) -> Dict:
        """Query AlienVault OTX for IP intelligence."""
        result = {"source": "AlienVault OTX (IP)", "found": False, "data": {}}

        try:
            resp = self.session.get(
                f"https://otx.alienvault.com/api/v1/indicators/IPv4/{target}/general",
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json()
                result["found"] = True
                result["data"]["pulse_count"] = data.get("pulse_info", {}).get("count", 0)
                result["data"]["reputation"] = data.get("reputation", 0)
                result["data"]["geo"] = data.get("geo", {})
                result["data"]["pulses"] = [
                    {
                        "name": p.get("name", ""),
                        "description": (p.get("description", "") or "")[:200],
                        "tags": p.get("tags", []),
                    }
                    for p in data.get("pulse_info", {}).get("pulses", [])[:10]
                ]
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute threat intelligence gathering from multiple feeds.
        Target can be a domain or IP address.
        """
        start = time.time()

        results = {
            "target": target,
            "feeds": {},
            "threat_score": 0,
            "malicious_indicators": [],
            "summary": {},
        }

        import ipaddress

        # Determine if target is IP or domain
        try:
            ipaddress.ip_address(target)
            target_type = "ip"
        except ValueError:
            target_type = "domain"

        results["target_type"] = target_type

        # Query URLScan
        try:
            results["feeds"]["urlscan"] = self._urlscan_lookup(target)
        except Exception as e:
            results["feeds"]["urlscan"] = {"error": str(e)[:100]}

        # Query VirusTotal
        try:
            results["feeds"]["virustotal"] = self._virustotal_lookup(target)
        except Exception as e:
            results["feeds"]["virustotal"] = {"error": str(e)[:100]}

        # Query AlienVault
        try:
            if target_type == "ip":
                results["feeds"]["alienvault"] = self._alienvault_ip_lookup(target)
            else:
                results["feeds"]["alienvault"] = self._alienvault_lookup(target)
        except Exception as e:
            results["feeds"]["alienvault"] = {"error": str(e)[:100]}

        # Calculate threat score
        threat_indicators = 0
        sources_checked = 0
        for feed_name, feed_data in results["feeds"].items():
            if feed_data.get("found") or feed_data.get("data"):
                sources_checked += 1
                # Check for malicious indicators
                if "malicious_scans" in feed_data.get("data", {}):
                    threat_indicators += feed_data["data"]["malicious_scans"]
                if "pulse_count" in feed_data.get("data", {}):
                    threat_indicators += feed_data["data"]["pulse_count"]
                if "last_analysis_stats" in feed_data.get("data", {}):
                    stats = feed_data["data"]["last_analysis_stats"]
                    threat_indicators += stats.get("malicious", 0) + stats.get("suspicious", 0)

        results["threat_score"] = min(threat_indicators, 100)
        results["summary"] = {
            "sources_checked": sources_checked,
            "threat_indicators": threat_indicators,
            "threat_score": results["threat_score"],
            "risk_level": "Critical" if results["threat_score"] > 50
            else "High" if results["threat_score"] > 20
            else "Medium" if results["threat_score"] > 5
            else "Low" if results["threat_score"] > 0
            else "None Detected",
        }

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
