"""
Reverse Image Search Module
Performs reverse image searches across multiple engines and extracts metadata.
"""

import requests
import time
import base64
import os
import json
from typing import Dict, List, Optional
from urllib.parse import quote
from .base import OSINTModule, ModuleResult


class ReverseImageIntel(OSINTModule):
    """Reverse image search - finds image origins, related images, and contextual data."""

    name = "reverse_image"
    description = "Reverse image search across engines - origin finding, similar images, metadata"

    # Reverse image search engines (clearnet)
    ENGINES = {
        "Google Images": {
            "url": "https://images.google.com/searchbyimage?image_url={url}",
            "type": "url",
        },
        "TinEye": {
            "url": "https://tineye.com/search?url={url}",
            "type": "url",
        },
        "Bing Images": {
            "url": "https://www.bing.com/images/search?q=imgurl:{url}&view=detailv2",
            "type": "url",
        },
        "Yandex Images": {
            "url": "https://yandex.com/images/search?url={url}&rpt=imageview",
            "type": "url",
        },
    }

    # Common image metadata extraction endpoints
    EXIF_TOOLS = [
        "https://exifinfo.org/api/extract",
    ]

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def _is_url(self, target: str) -> bool:
        """Check if target is a URL."""
        return target.startswith(("http://", "https://"))

    def _is_file_path(self, target: str) -> bool:
        """Check if target is a local file path."""
        return os.path.exists(target)

    def _generate_search_links(self, target: str) -> Dict[str, str]:
        """Generate reverse image search links for all engines."""
        links = {}
        encoded = quote(target, safe="")
        for engine, config in self.ENGINES.items():
            try:
                links[engine] = config["url"].format(url=encoded)
            except Exception:
                continue
        return links

    def _check_engine(self, name: str, url: str) -> Dict:
        """Check if a reverse image search engine is accessible."""
        try:
            resp = self.session.head(url, timeout=10, allow_redirects=True)
            return {
                "engine": name,
                "url": url,
                "accessible": resp.status_code < 500,
                "status_code": resp.status_code,
            }
        except Exception as e:
            return {
                "engine": name,
                "url": url,
                "accessible": False,
                "error": str(e)[:100],
            }

    def _extract_metadata_from_file(self, filepath: str) -> Dict:
        """Extract EXIF and metadata from an image file using Python."""
        metadata = {
            "filename": os.path.basename(filepath),
            "size_bytes": os.path.getsize(filepath),
            "exif": {},
            "error": None,
        }

        try:
            # Try using PIL/Pillow for EXIF
            from PIL import Image
            from PIL.ExifTags import TAGS

            img = Image.open(filepath)
            metadata["format"] = img.format
            metadata["mode"] = img.mode
            metadata["width"] = img.width
            metadata["height"] = img.height

            exif_data = img._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="replace")
                        except Exception:
                            value = str(value)
                    metadata["exif"][tag_name] = str(value)[:200]
        except ImportError:
            metadata["error"] = "Pillow not installed; basic file stats only"
        except Exception as e:
            metadata["error"] = str(e)[:100]

        return metadata

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute reverse image search.
        Target can be an image URL or a local file path.
        """
        start = time.time()

        results = {
            "target": target,
            "target_type": "unknown",
            "search_links": {},
            "engine_accessibility": [],
            "metadata": {},
        }

        if self._is_url(target):
            results["target_type"] = "url"
            # Generate search links for all engines
            results["search_links"] = self._generate_search_links(target)

            # Check which engines are accessible
            for engine, link in results["search_links"].items():
                check = self._check_engine(engine, link)
                results["engine_accessibility"].append(check)

        elif self._is_file_path(target):
            results["target_type"] = "local_file"
            # Extract metadata from local file
            results["metadata"] = self._extract_metadata_from_file(target)

            # If it's a local file, we can't directly reverse search it without uploading
            results["note"] = (
                "For reverse search of local files, upload to an image host "
                "and use the resulting URL as target."
            )
        else:
            results["target_type"] = "unknown"
            results["error"] = (
                "Target must be an image URL (http:// or https://) or a valid local file path"
            )

        duration = (time.time() - start) * 1000
        return self._success(results, duration)
