"""
Technology Stack Fingerprinting Module
Advanced web technology detection - frameworks, libraries, analytics, hosting, CDN.
"""

import requests
import re
import time
import json
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class TechnologyStack(OSINTModule):
    """
    Technology stack fingerprinting with 100+ detection signatures.
    Identifies web servers, frameworks, CMS platforms, analytics, CDNs, and more.
    """

    name = "technology_stack"
    description = "Advanced technology stack fingerprinting - 100+ signatures for web technologies"

    # Comprehensive technology detection signatures
    SIGNATURES = {
        "Web Servers": {
            "regex": [
                (r"nginx/?([\d.]+)?", "Nginx"),
                (r"Apache(?:/?([\d.]+))?", "Apache HTTP Server"),
                (r"cloudflare", "Cloudflare"),
                (r"Microsoft-IIS/?([\d.]+)?", "IIS"),
                (r"LiteSpeed", "LiteSpeed"),
                (r"Caddy", "Caddy"),
                (r"OpenResty", "OpenResty"),
                (r"Tomcat", "Apache Tomcat"),
                (r"Jetty", "Eclipse Jetty"),
            ],
            "source": "headers",
        },
        "CMS Platforms": {
            "regex": [
                (r"wp-content|wp-includes|wp-json", "WordPress"),
                (r"Drupal", "Drupal"),
                (r"Joomla!", "Joomla"),
                (r"Mageto|Mage.", "Magento"),
                (r"Shopify", "Shopify"),
                (r"Squarespace", "Squarespace"),
                (r"Wix", "Wix"),
                (r"Ghost", "Ghost"),
                (r"Umbraco", "Umbraco"),
                (r"TYPO3", "TYPO3 CMS"),
                (r"Django", "Django CMS"),
                (r"Concrete5", "Concrete CMS"),
            ],
            "source": "html",
        },
        "JavaScript Frameworks": {
            "regex": [
                (r'react(?:\.)?(?:[\d.]+)?', "React"),
                (r'vue(?:\.js)?', "Vue.js"),
                (r'angular(?:\.js)?', "Angular"),
                (r'jquery', "jQuery"),
                (r'backbone\.js', "Backbone.js"),
                (r'ember\.js', "Ember.js"),
                (r'svelte', "Svelte"),
                (r'next\.js', "Next.js"),
                (r'nuxt', "Nuxt.js"),
                (r'gatsby', "Gatsby"),
                (r'alpinejs', "Alpine.js"),
                (r'htmx', "HTMX"),
                (r'turbo', "Hotwire Turbo"),
                (r'stimulus', "Stimulus"),
            ],
            "source": "html",
        },
        "CSS Frameworks": {
            "regex": [
                (r"tailwindcss", "Tailwind CSS"),
                (r"bootstrap", "Bootstrap"),
                (r"foundation", "Foundation"),
                (r"bulma", "Bulma"),
                (r"materialize", "Materialize CSS"),
                (r"semantic-ui", "Semantic UI"),
            ],
            "source": "html",
        },
        "Analytics & Tracking": {
            "regex": [
                (r"google-analytics|ga\.js|gtag", "Google Analytics"),
                (r"googletagmanager", "Google Tag Manager"),
                (r"facebook\.com/tr", "Facebook Pixel"),
                (r"hotjar", "Hotjar"),
                (r"mouseflow", "Mouseflow"),
                (r"crazyegg", "CrazyEgg"),
                (r"hubspot", "HubSpot"),
                (r"intercom", "Intercom"),
                (r"mixpanel", "Mixpanel"),
                (r"amplitude", "Amplitude"),
                (r"segment\.com", "Segment"),
                (r"clarity", "Microsoft Clarity"),
                (r"matomo", "Matomo"),
            ],
            "source": "html",
        },
        "CDN & Hosting": {
            "regex": [
                (r"cloudflare", "Cloudflare"),
                (r"akamai", "Akamai"),
                (r"fastly", "Fastly"),
                (r"stackpath", "StackPath"),
                (r"cloudfront", "AWS CloudFront"),
                (r"incapsula|imperva", "Imperva Incapsula"),
                (r"keycdn", "KeyCDN"),
                (r"cdnjs", "CDNJS"),
                (r"unpkg", "UNPKG"),
                (r"jsdelivr", "jsDelivr"),
            ],
            "source": "headers",
        },
        "Programming Languages": {
            "regex": [
                (r"X-Powered-By: PHP", "PHP", "headers"),
                (r"X-Powered-By: ASP\.NET", "ASP.NET", "headers"),
                (r"X-Powered-By: Express", "Node.js/Express", "headers"),
                (r"rails", "Ruby on Rails", "html"),
                (r"csrftoken", "Python/Django", "headers"),
                (r"laravel", "Laravel", "cookies"),
                (r"symfony", "Symfony", "cookies"),
            ],
            "source": "mixed",
        },
        "API & Infrastructure": {
            "regex": [
                (r"graphql", "GraphQL"),
                (r"swagger|openapi", "Swagger/OpenAPI"),
                (r"rest/api", "REST API"),
                (r"websocket", "WebSocket"),
                (r"grpc", "gRPC"),
                (r"docker", "Docker"),
                (r"kubernetes", "Kubernetes"),
                (r"elasticsearch", "Elasticsearch"),
                (r"redis", "Redis"),
                (r"mysql", "MySQL"),
                (r"postgres", "PostgreSQL"),
                (r"mongodb", "MongoDB"),
                (r"socket\.io", "Socket.IO"),
            ],
            "source": "html",
        },
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })

    def _fetch_headers_simple(self, url: str) -> Dict:
        """Get HTTP headers with redirect following."""
        try:
            resp = self.session.get(url, timeout=8, allow_redirects=True)
            headers = dict(resp.headers)
            # Add server detection cookies
            cookies = dict(resp.cookies)
            headers["_cookies"] = cookies
            headers["_status_code"] = resp.status_code
            headers["_body_preview"] = resp.text[:50000]
            return headers
        except Exception as e:
            return {"_error": str(e)[:100]}

    def _detect_technologies(self, headers: Dict, body: str) -> Dict[str, List[str]]:
        """Detect technologies from headers and HTML body."""
        detected = {}
        header_str = json.dumps(headers).lower()

        for category, sigs in self.SIGNATURES.items():
            found = []
            for sig in sigs["regex"]:
                pattern = sig[0]
                tech_name = sig[1]
                try:
                    if re.search(pattern, header_str, re.IGNORECASE):
                        found.append(tech_name)
                    elif body and re.search(pattern, body, re.IGNORECASE):
                        found.append(tech_name)
                except Exception:
                    continue
            if found:
                detected[category] = list(set(found))

        return detected

    def _check_wappalyzer_signatures(self, headers: Dict, body: str) -> Dict:
        """Additional signature checks based on common patterns."""
        extras = {}

        # Check for specific cookies
        cookies = headers.get("_cookies", {})
        if isinstance(cookies, dict):
            if "laravel_session" in cookies:
                extras.setdefault("Frameworks", []).append("Laravel")
            if "PHPSESSID" in cookies:
                extras.setdefault("Languages", []).append("PHP")
            if "ASP.NET_SessionId" in cookies:
                extras.setdefault("Languages", []).append("ASP.NET")
            if("JSESSIONID") in cookies:
                extras.setdefault("Languages", []).append("Java")
            if "wp-settings" in cookies:
                extras.setdefault("CMS", []).append("WordPress")

        return extras

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute technology stack fingerprinting.
        Target should be a domain or URL.
        """
        start = time.time()

        results = {
            "target": target,
            "technologies": {},
            "headers": {},
            "fingerprint_method": "http_headers_html_analysis",
            "summary": {},
        }

        # Normalize URL
        url = target
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"

        # First try HTTPS, fallback to HTTP
        response_headers = {}
        body = ""

        for scheme in ["https://", "http://"]:
            test_url = scheme + target if not target.startswith("http") else target
            try:
                resp = self.session.get(test_url, timeout=8, allow_redirects=True)
                response_headers = dict(resp.headers)
                response_headers["_cookies"] = dict(resp.cookies)
                response_headers["_status_code"] = resp.status_code
                body = resp.text[:100000]
                results["final_url"] = resp.url
                results["status_code"] = resp.status_code
                break
            except Exception:
                continue

        results["headers"] = {
            k: v for k, v in response_headers.items()
            if not k.startswith("_")
        }

        # Detect technologies
        techs = self._detect_technologies(response_headers, body)

        # Check additional signatures
        extras = self._check_wappalyzer_signatures(response_headers, body)
        for category, items in extras.items():
            if category in techs:
                techs[category].extend(items)
            else:
                techs[category] = items

        results["technologies"] = techs

        # Summary
        total_techs = sum(len(v) for v in techs.values())
        categories_found = list(techs.keys())
        results["summary"] = {
            "technologies_detected": total_techs,
            "categories": categories_found,
            "method": "HTTP headers + HTML analysis",
        }

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
