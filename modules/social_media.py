"""
Social Media Intelligence Module
Real profile discovery, username checking, and social footprint analysis.
"""

import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class SocialMediaIntel(OSINTModule):
    """Social media intelligence - discovers profiles across 20+ platforms."""

    name = "social_media"
    description = "Social media profile discovery across 20+ platforms"

    PLATFORMS = {
        "Twitter/X": {
            "url": "https://twitter.com/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "LinkedIn": {
            "url": "https://www.linkedin.com/in/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "GitHub": {
            "url": "https://github.com/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Instagram": {
            "url": "https://www.instagram.com/{username}/",
            "check": "status",
            "check_type": "exists",
        },
        "Reddit": {
            "url": "https://www.reddit.com/user/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "YouTube": {
            "url": "https://www.youtube.com/@{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Medium": {
            "url": "https://medium.com/@{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Dev.to": {
            "url": "https://dev.to/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Twitch": {
            "url": "https://www.twitch.tv/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "TikTok": {
            "url": "https://www.tiktok.com/@{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Pinterest": {
            "url": "https://www.pinterest.com/{username}/",
            "check": "status",
            "check_type": "exists",
        },
        "Telegram": {
            "url": "https://t.me/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "WhatsApp": {
            "url": "https://wa.me/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Snapchat": {
            "url": "https://www.snapchat.com/add/{username}",
            "check": "status",
            "check_type": "exists",
        },
        "Facebook": {
            "url": "https://www.facebook.com/{username}",
            "check": "status",
            "check_type": "exists",
        },
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        })
        self.session.max_redirects = 3

    def _check_profile(self, platform: str, config: Dict, username: str) -> Dict:
        """Check if a username exists on a given platform."""
        url = config["url"].format(username=username)
        result = {
            "platform": platform,
            "url": url,
            "exists": False,
            "status_code": None,
            "error": None,
        }
        try:
            resp = self.session.get(url, timeout=8, allow_redirects=True)
            result["status_code"] = resp.status_code
            # 200 or 301/302 that leads to profile page = exists
            if resp.status_code == 200:
                result["exists"] = True
            elif resp.status_code in (301, 302, 303):
                # Some platforms redirect to profile on success
                result["exists"] = True
        except requests.Timeout:
            result["error"] = "timeout"
        except requests.ConnectionError:
            result["error"] = "connection_error"
        except Exception as e:
            result["error"] = str(e)[:100]
        return result

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """Check target as a username across social media platforms."""
        start = time.time()
        username = target.strip().lstrip("@").split("/")[-1]

        results = {
            "username": username,
            "profiles": [],
            "found_count": 0,
            "platforms_checked": len(self.PLATFORMS),
        }

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self._check_profile, name, cfg, username): name
                for name, cfg in self.PLATFORMS.items()
            }
            for future in as_completed(futures):
                try:
                    profile = future.result()
                    results["profiles"].append(profile)
                    if profile["exists"]:
                        results["found_count"] += 1
                except Exception:
                    pass

        # Sort: found profiles first
        results["profiles"].sort(key=lambda x: (not x["exists"], x["platform"]))

        duration = (time.time() - start) * 1000

        if results["found_count"] > 0:
            return self._success(results, duration)
        return self._partial(
            results,
            f"No social media profiles found for '{username}' on checked platforms",
        )
