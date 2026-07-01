"""
Data Breach Intelligence Module
Checks for compromised credentials, data breaches, and leaked information.
"""

import requests
import re
import time
import hashlib
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class BreachIntel(OSINTModule):
    """Data breach intelligence - credential leaks, breach databases, password exposure."""

    name = "breach_intel"
    description = "Data breach intelligence - credential leak checking, breach history, password exposure"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "OmniSightAI-BreachIntel/2.0",
        })
        self.haveibeenpwned_api = "https://haveibeenpwned.com/api/v3"

    def _hibp_check_email(self, email: str) -> Dict:
        """Check email against HaveIBeenPwned (using k-anonymity model for passwords)."""
        result = {
            "email": email,
            "breaches": [],
            "pastes": [],
            "error": None,
        }

        # Check for breaches (requires API key for v3, v2 is public but rate-limited)
        try:
            resp = self.session.get(
                f"{self.haveibeenpwned_api}/breachedaccount/{email}",
                headers={"hibp-api-key": ""},  # Add key if available
                timeout=10,
            )
            if resp.status_code == 200:
                breaches = resp.json()
                for breach in breaches:
                    result["breaches"].append({
                        "name": breach.get("Name", ""),
                        "domain": breach.get("Domain", ""),
                        "date": breach.get("BreachDate", ""),
                        "data_classes": breach.get("DataClasses", []),
                        "description": breach.get("Description", "")[:200],
                    })
            elif resp.status_code == 404:
                pass  # No breaches found
            elif resp.status_code == 429:
                result["error"] = "Rate limited by HIBP API"
        except Exception as e:
            result["error"] = str(e)[:100]

        return result

    def _check_password_exposure(self, password_hash: str) -> Dict:
        """Check if a password hash appears in known breaches using k-anonymity."""
        result = {
            "hash_prefix": password_hash[:5],
            "exposed": False,
            "count": 0,
        }

        if len(password_hash) < 5:
            return result

        try:
            resp = self.session.get(
                f"https://api.pwnedpasswords.com/range/{password_hash[:5]}",
                timeout=10,
            )
            if resp.status_code == 200:
                suffix = password_hash[5:].upper()
                for line in resp.text.splitlines():
                    if line.startswith(suffix):
                        count = int(line.split(":")[1])
                        result["exposed"] = True
                        result["count"] = count
                        break
        except Exception:
            pass

        return result

    def _scan_public_sources(self, target: str) -> List[Dict]:
        """Scan public sources for leaked credentials."""
        findings = []

        # Check public paste sites for target
        paste_apis = [
            f"https://psbdmp.ws/api/v3/search?q={target}",
        ]

        for api_url in paste_apis:
            try:
                resp = self.session.get(api_url, timeout=10)
                if resp.status_code == 200:
                    data = resp.json()
                    findings.append({
                        "source": api_url.split("/")[2],
                        "entries_found": len(data) if isinstance(data, list) else 1,
                        "status": "found" if data else "empty",
                    })
            except Exception:
                continue

        return findings

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute breach intelligence.
        Target can be an email address, username, or domain.
        """
        start = time.time()

        results = {
            "target": target,
            "target_type": "unknown",
            "email_breaches": [],
            "password_exposure": {},
            "public_leaks": [],
            "summary": {},
        }

        # Determine target type
        if "@" in target:
            results["target_type"] = "email"
            # Check email breaches
            breach_data = self._hibp_check_email(target)
            results["email_breaches"].append(breach_data)

            # Check password exposure for common password hashes
            for common_pw in ["password", "123456", "admin", target.split("@")[0]]:
                pw_hash = hashlib.sha1(common_pw.encode()).hexdigest().upper()
                exposure = self._check_password_exposure(pw_hash)
                if exposure["exposed"]:
                    results["password_exposure"][common_pw] = exposure

        elif re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", target):
            results["target_type"] = "email"
            breach_data = self._hibp_check_email(target)
            results["email_breaches"].append(breach_data)

        else:
            results["target_type"] = "domain_or_username"
            # Try as username - check leak sources
            public_findings = self._scan_public_sources(target)
            results["public_leaks"] = public_findings

        # Summary
        total_breaches = sum(
            len(b.get("breaches", [])) for b in results["email_breaches"]
        )
        results["summary"] = {
            "breaches_found": total_breaches,
            "password_exposures": len(results["password_exposure"]),
            "public_leaks_found": len(results["public_leaks"]),
        }

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
