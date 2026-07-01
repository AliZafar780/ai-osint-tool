"""
SSL/TLS Certificate Analysis Module
Analyzes SSL certificates, security configurations, and protocol support.
"""

import time
import socket
import ssl
import json
from datetime import datetime
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class SSLAnalysis(OSINTModule):
    """SSL/TLS certificate analysis - security assessment, protocol support, certificate details."""

    name = "ssl_analysis"
    description = "SSL/TLS certificate analysis - certificate details, security, protocol support"

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)

    def _get_certificate(self, hostname: str, port: int = 443) -> Dict:
        """Retrieve SSL certificate from a host."""
        result = {
            "hostname": hostname,
            "port": port,
            "certificate": {},
            "error": None,
        }

        try:
            context = ssl.create_default_context()
            context.check_hostname = True
            context.verify_mode = ssl.CERT_REQUIRED

            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert(binary_form=True)
                    # Parse using SSL module
                    import cryptography
                    from cryptography import x509
                    from cryptography.hazmat.backends import default_backend
                    from cryptography.hazmat.primitives import hashes

                    parsed = x509.load_der_x509_certificate(cert, default_backend())

                    # Extract common fields
                    subject = parsed.subject
                    issuer = parsed.issuer
                    result["certificate"] = {
                        "subject": {
                            attr.oid._name: attr.value
                            for attr in subject
                        },
                        "issuer": {
                            attr.oid._name: attr.value
                            for attr in issuer
                        },
                        "serial_number": str(parsed.serial_number),
                        "not_valid_before": parsed.not_valid_before_utc.isoformat(),
                        "not_valid_after": parsed.not_valid_after_utc.isoformat(),
                        "signature_algorithm": parsed.signature_algorithm_oid._name,
                        "version": parsed.version.value,
                    }

                    # Check if it's self-signed
                    if subject == issuer:
                        result["certificate"]["self_signed"] = True
                    else:
                        result["certificate"]["self_signed"] = False

                    # SANs (Subject Alternative Names)
                    try:
                        san_ext = parsed.extensions.get_extension_for_class(
                            x509.SubjectAlternativeName
                        )
                        sans = san_ext.value.get_values_for_type(x509.DNSName)
                        result["certificate"]["subject_alt_names"] = sans
                    except cryptography.x509.ExtensionNotFound:
                        result["certificate"]["subject_alt_names"] = []

                    # Extended Validation check
                    try:
                        result["certificate"]["is_ev"] = bool(
                            parsed.extensions.get_extension_for_oid(
                                x509.oid.ExtensionOID.CERTIFICATE_POLICIES
                            )
                        )
                    except Exception:
                        result["certificate"]["is_ev"] = False

        except ssl.SSLCertVerificationError as e:
            result["error"] = f"SSL verification failed: {e}"
            # Still try to get certificate without verification
            self._get_certificate_no_verify(hostname, port, result)
        except socket.timeout:
            result["error"] = "Connection timed out"
        except ConnectionRefusedError:
            result["error"] = "Connection refused"
        except ImportError:
            result["error"] = "cryptography package required for full SSL analysis"
        except Exception as e:
            result["error"] = str(e)[:200]

        return result

    def _get_certificate_no_verify(self, hostname: str, port: int, result: Dict):
        """Fallback: get certificate without verification."""
        try:
            context = ssl._create_unverified_context()
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert_bin = ssock.getpeercert(binary_form=True)
                    if cert_bin:
                        result["certificate"]["raw_available"] = True
                        result["certificate"]["verified"] = False
        except Exception:
            pass

    def _check_protocols(self, hostname: str) -> Dict:
        """Check supported SSL/TLS protocol versions."""
        protocols = {
            "SSLv2": False,
            "SSLv3": False,
            "TLSv1.0": False,
            "TLSv1.1": False,
            "TLSv1.2": True,  # Assume supported
            "TLSv1.3": True,  # Assume supported
        }

        # Test TLS 1.0
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = ssl.TLSVersion.TLSv1
            context.maximum_version = ssl.TLSVersion.TLSv1
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    protocols["TLSv1.0"] = True
        except Exception:
            protocols["TLSv1.0"] = False

        # Test TLS 1.1
        try:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.minimum_version = ssl.TLSVersion.TLSv1_1
            context.maximum_version = ssl.TLSVersion.TLSv1_1
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((hostname, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    protocols["TLSv1.1"] = True
        except Exception:
            protocols["TLSv1.1"] = False

        # Remove protocols that are disabled
        for proto in ["SSLv2", "SSLv3", "TLSv1.0", "TLSv1.1"]:
            if not protocols[proto]:
                del protocols[proto]

        return protocols

    def _check_security_headers(self, hostname: str) -> Dict:
        """Check HTTP security headers over HTTPS."""
        headers_info = {}
        try:
            import requests

            resp = requests.get(
                f"https://{hostname}",
                timeout=10,
                verify=True,
                allow_redirects=True,
            )

            security_headers = {
                "Strict-Transport-Security": "HSTS",
                "Content-Security-Policy": "CSP",
                "X-Content-Type-Options": "XCTO",
                "X-Frame-Options": "XFO",
                "X-XSS-Protection": "XXSSP",
                "Referrer-Policy": "Referrer-Policy",
                "Permissions-Policy": "Permissions-Policy",
            }

            for header, name in security_headers.items():
                if header.lower() in {k.lower(): v for k, v in resp.headers.items()}:
                    actual_value = resp.headers.get(header)
                    headers_info[header] = actual_value
                else:
                    headers_info[header] = None

            headers_info["_status_code"] = resp.status_code

        except Exception as e:
            headers_info["error"] = str(e)[:100]

        return headers_info

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute SSL/TLS analysis.
        Target can be a hostname (e.g., example.com) or hostname:port.
        """
        start = time.time()

        results = {
            "target": target,
            "certificate_info": {},
            "protocols": {},
            "security_headers": {},
            "security_score": 0,
            "issues": [],
            "recommendations": [],
        }

        # Parse hostname and port
        hostname = target
        port = 443
        if ":" in target:
            parts = target.rsplit(":", 1)
            if parts[1].isdigit():
                hostname = parts[0]
                port = int(parts[1])

        results["resolved_host"] = hostname
        results["port"] = port

        # Get certificate details
        try:
            cert_info = self._get_certificate(hostname, port)
            results["certificate_info"] = cert_info
        except Exception as e:
            results["certificate_info"] = {"error": str(e)[:200]}

        # Check protocols
        try:
            results["protocols"] = self._check_protocols(hostname)
        except Exception as e:
            results["protocols"] = {"error": str(e)[:100]}

        # Check security headers
        try:
            results["security_headers"] = self._check_security_headers(hostname)
        except Exception as e:
            results["security_headers"] = {"error": str(e)[:100]}

        # Calculate security score
        score = 100
        issues = []
        recommendations = []

        cert_data = results["certificate_info"].get("certificate", {})
        if cert_data:
            # Check expiration
            if "not_valid_after" in cert_data:
                try:
                    from datetime import datetime as dt
                    expires = dt.fromisoformat(
                        cert_data["not_valid_after"].replace("Z", "+00:00")
                    )
                    if expires < dt.now().astimezone():
                        score -= 30
                        issues.append("Certificate is expired!")
                        recommendations.append("Renew the SSL certificate immediately")
                except Exception:
                    pass

            if cert_data.get("self_signed"):
                score -= 15
                issues.append("Self-signed certificate in use")
                recommendations.append("Replace self-signed certificate with CA-signed one")

        # Check for outdated protocols
        if results["protocols"].get("SSLv3"):
            score -= 25
            issues.append("Obsolete SSLv3 protocol supported (POODLE vulnerability)")
            recommendations.append("Disable SSLv3 immediately")

        if results["protocols"].get("TLSv1.0"):
            score -= 15
            issues.append("Deprecated TLS v1.0 supported")
            recommendations.append("Disable TLS 1.0, use TLS 1.2+")

        if results["protocols"].get("TLSv1.1"):
            score -= 10
            issues.append("Deprecated TLS v1.1 supported")
            recommendations.append("Disable TLS 1.1, use TLS 1.2+")

        # Check security headers
        hdrs = results["security_headers"]
        if hdrs.get("Strict-Transport-Security") is None:
            score -= 5
            issues.append("Missing HSTS header")
            recommendations.append("Add Strict-Transport-Security header")
        if hdrs.get("Content-Security-Policy") is None:
            score -= 5
            issues.append("Missing Content-Security-Policy header")
            recommendations.append("Add CSP header to mitigate XSS")
        if hdrs.get("X-Content-Type-Options") is None:
            score -= 3
            recommendations.append("Add X-Content-Type-Options: nosniff")

        results["security_score"] = max(0, score)
        results["issues"] = issues
        results["recommendations"] = recommendations
        results["grade"] = (
            "A" if score >= 80 else
            "B" if score >= 60 else
            "C" if score >= 40 else
            "D" if score >= 20 else
            "F"
        )

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
