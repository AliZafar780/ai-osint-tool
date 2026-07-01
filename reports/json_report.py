"""
JSON Report Generator
Generates structured JSON reports for machine parsing and integration.
"""

import json
from datetime import datetime
from typing import Any, Dict, Optional
from .base_report import BaseReportGenerator


class JSONReportGenerator(BaseReportGenerator):
    """Generates structured JSON reports."""

    name = "json"
    extension = ".json"
    description = "Structured JSON report for machine parsing"

    def generate(
        self, target: str, results: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Generate JSON report file."""
        filepath = self._get_filepath(target, filename)

        report = {
            "metadata": self._metadata_block(target),
            "target": target,
            "modules": {},
            "summary": {
                "total_modules": len(results),
                "successful_modules": 0,
                "failed_modules": 0,
                "findings_count": 0,
            },
        }

        for module_name, module_result in results.items():
            module_data = {
                "status": "unknown",
                "data": {},
                "error": None,
                "duration_ms": None,
            }

            if isinstance(module_result, dict):
                module_data["status"] = module_result.get("status", "completed")
                module_data["data"] = module_result.get("data", module_result)
                module_data["error"] = module_result.get("error")
                module_data["duration_ms"] = module_result.get("duration_ms")

                if module_data["status"] == "completed":
                    report["summary"]["successful_modules"] += 1
                elif module_data["status"] == "failed":
                    report["summary"]["failed_modules"] += 1

            report["modules"][module_name] = module_data

        # Count findings
        findings = 0
        for mod_name, mod_data in report["modules"].items():
            data = mod_data.get("data", {})
            if isinstance(data, dict):
                for key, val in data.items():
                    if isinstance(val, list):
                        findings += len(val)
                    elif isinstance(val, dict):
                        findings += len(val)
            elif isinstance(data, list):
                findings += len(data)
            elif data:
                findings += 1
        report["summary"]["findings_count"] = findings

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        except OSError as e:
            raise IOError(f"Failed to write JSON report: {e}")

        return filepath
