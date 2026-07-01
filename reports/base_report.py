"""
Base Report Generator
Common interface for all report output formats.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import os


class BaseReportGenerator:
    """Base class for report generators."""

    name = "base"
    extension = ".txt"
    description = "Base report format"

    def __init__(self, output_dir: str = "./osint_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(
        self, target: str, results: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Generate report and return file path."""
        raise NotImplementedError

    def _sanitize_filename(self, target: str) -> str:
        """Create a safe filename from target."""
        safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in target)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"osint_report_{safe}_{timestamp}"

    def _get_filepath(self, target: str, filename: Optional[str] = None) -> str:
        """Get full file path for report."""
        if filename:
            fname = filename
        else:
            fname = self._sanitize_filename(target) + self.extension
        return os.path.join(self.output_dir, fname)

    def _metadata_block(self, target: str) -> Dict:
        """Generate metadata for report header."""
        return {
            "report_title": "OmniSight AI - Comprehensive OSINT Report",
            "target": target,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "generator": "OmniSight AI v2.0",
            "generator_url": "https://github.com/AliZafar780/ai-osint-tool",
        }
