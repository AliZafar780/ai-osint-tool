"""
HTML Report Generator
Generates professional HTML reports with styling and interactive elements.
"""

import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from .base_report import BaseReportGenerator


class HTMLReportGenerator(BaseReportGenerator):
    """Generates professional HTML reports with CSS styling."""

    name = "html"
    extension = ".html"
    description = "Professional HTML report with styling"

    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniSight AI - OSINT Report: {target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, sans-serif;
            background: #0a0e17;
            color: #e0e0e0;
            line-height: 1.6;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{
            background: linear-gradient(135deg, #00d4ff 0%, #0072ff 50%, #090979 100%);
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{ color: #fff; font-size: 2.2em; margin-bottom: 10px; }}
        .header p {{ color: rgba(255,255,255,0.85); font-size: 1.1em; }}
        .header .meta {{ color: rgba(255,255,255,0.7); font-size: 0.9em; margin-top: 10px; }}
        .module {{
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 10px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .module-header {{
            background: #1a2332;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #1e293b;
        }}
        .module-header:hover {{ background: #1e293b; }}
        .module-header h3 {{ color: #00d4ff; font-size: 1.1em; }}
        .module-header .status {{
            padding: 3px 12px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: 600;
        }}
        .status-completed {{ background: #065f46; color: #6ee7b7; }}
        .status-failed {{ background: #7f1d1d; color: #fca5a5; }}
        .status-partial {{ background: #78350f; color: #fcd34d; }}
        .status-skipped {{ background: #374151; color: #9ca3af; }}
        .module-content {{ padding: 20px; display: none; }}
        .module-content.active {{ display: block; }}
        .data-table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        .data-table th {{
            text-align: left;
            padding: 8px 12px;
            background: #1a2332;
            color: #00d4ff;
            border-bottom: 1px solid #1e293b;
            font-weight: 500;
        }}
        .data-table td {{
            padding: 8px 12px;
            border-bottom: 1px solid #1e293b;
            color: #d1d5db;
        }}
        .data-table tr:hover td {{ background: #1a2332; }}
        .key-value {{
            display: flex;
            padding: 6px 0;
            border-bottom: 1px solid #1a2332;
        }}
        .key {{ color: #00d4ff; min-width: 200px; font-weight: 500; }}
        .value {{ color: #d1d5db; flex: 1; word-break: break-all; }}
        .error-box {{
            background: #7f1d1d;
            border: 1px solid #dc2626;
            padding: 10px 15px;
            border-radius: 6px;
            color: #fca5a5;
            margin: 10px 0;
        }}
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        .summary-card {{
            background: #1a2332;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card .number {{ font-size: 2em; color: #00d4ff; font-weight: 700; }}
        .summary-card .label {{ color: #9ca3af; font-size: 0.85em; margin-top: 5px; }}
        .footer {{
            text-align: center;
            padding: 30px;
            color: #6b7280;
            font-size: 0.85em;
        }}
        .tag {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            margin: 2px;
            background: #1e293b;
            color: #00d4ff;
        }}
        pre {{ background: #0a0e17; padding: 15px; border-radius: 6px; overflow-x: auto; font-size: 0.9em; }}
        @media (max-width: 768px) {{ .key {{ min-width: 120px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>OmniSight AI - OSINT Report</h1>
            <p>Target: <strong>{target}</strong></p>
            <div class="meta">
                Generated: {timestamp}<br>
                Tool: <a href="https://github.com/AliZafar780/ai-osint-tool" style="color: #93c5fd;">OmniSight AI v2.0</a>
            </div>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="number">{total_modules}</div>
                <div class="label">Modules Executed</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color: #6ee7b7;">{successful}</div>
                <div class="label">Successful</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color: #fca5a5;">{failed}</div>
                <div class="label">Failed/Skipped</div>
            </div>
            <div class="summary-card">
                <div class="number" style="color: #fcd34d;">{findings}</div>
                <div class="label">Total Findings</div>
            </div>
        </div>

        {modules_html}

        <div class="footer">
            <p>OmniSight AI v2.0 — Advanced OSINT with AI Integration</p>
            <p>See everything, know everything. Use responsibly.</p>
        </div>
    </div>

    <script>
        document.querySelectorAll('.module-header').forEach(header => {{
            header.addEventListener('click', () => {{
                const content = header.nextElementSibling;
                content.classList.toggle('active');
            }});
        }});
    </script>
</body>
</html>
"""

    def generate(
        self, target: str, results: Dict[str, Any], filename: Optional[str] = None
    ) -> str:
        """Generate HTML report file."""
        filepath = self._get_filepath(target, filename)

        modules_html = []
        total_modules = len(results)
        successful = 0
        failed = 0
        findings = 0

        for module_name, module_result in results.items():
            if isinstance(module_result, dict):
                status = module_result.get("status", "completed")
                duration = module_result.get("duration_ms")
                error = module_result.get("error")
                data = module_result.get("data", module_result)
                
                if status == "completed":
                    successful += 1
                else:
                    failed += 1

                # Count findings
                if isinstance(data, dict):
                    for val in data.values():
                        if isinstance(val, list):
                            findings += len(val)
                        elif isinstance(val, dict):
                            findings += len(val)
                        elif val:
                            findings += 1
                elif isinstance(data, list):
                    findings += len(data)
                elif data:
                    findings += 1
            else:
                status = "unknown"
                data = module_result

            # Build module HTML
            md_html = f"""
            <div class="module">
                <div class="module-header">
                    <h3>{module_name}</h3>
                    <div>
                        <span class="status status-{status}">{status}</span>
                        {" <span style='color:#9ca3af;font-size:0.8em;'>" + f"{duration:.0f}ms" + "</span>" if isinstance(module_result, dict) and module_result.get("duration_ms") else ""}
                    </div>
                </div>
                <div class="module-content">
            """

            if isinstance(module_result, dict) and error:
                md_html += f'<div class="error-box">{error}</div>'

            md_html += self._format_data_html(data)
            md_html += "</div></div>"
            modules_html.append(md_html)

        report_html = self.HTML_TEMPLATE.format(
            target=target,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
            total_modules=total_modules,
            successful=successful,
            failed=failed,
            findings=findings,
            modules_html="\n".join(modules_html),
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(report_html)
        except OSError as e:
            raise IOError(f"Failed to write HTML report: {e}")

        return filepath

    def _format_data_html(self, data: Any, depth: int = 0) -> str:
        """Recursively format data as HTML."""
        if isinstance(data, dict):
            rows = []
            for key, value in data.items():
                if value is None or value == "" or value == [] or value == {}:
                    continue
                if key in ("error", "_error") and value:
                    rows.append(f'<div class="error-box">{value}</div>')
                elif isinstance(value, (dict, list)):
                    rows.append(f'<div class="key-value"><span class="key">{key}</span></div>')
                    rows.append(self._format_data_html(value, depth + 1))
                else:
                    val_str = str(value)[:500]
                    if isinstance(value, bool):
                        val_str = "Yes" if value else "No"
                    rows.append(
                        f'<div class="key-value"><span class="key">{key}</span>'
                        f'<span class="value">{self._escape(val_str)}</span></div>'
                    )
            return "\n".join(rows)

        elif isinstance(data, list):
            if all(isinstance(item, dict) for item in data[:10]):
                rows = ["<table class='data-table'><tr>"]
                # Collect all keys
                all_keys = set()
                for item in data[:50]:
                    all_keys.update(item.keys())
                all_keys = sorted(all_keys)
                for key in all_keys:
                    rows.append(f"<th>{key}</th>")
                rows.append("</tr>")
                for item in data[:50]:
                    rows.append("<tr>")
                    for key in all_keys:
                        val = str(item.get(key, ""))[:200]
                        rows.append(f"<td>{self._escape(val)}</td>")
                    rows.append("</tr>")
                rows.append("</table>")
                if len(data) > 50:
                    rows.append(f"<p style='color:#9ca3af;'>... and {len(data) - 50} more items</p>")
                return "\n".join(rows)
            else:
                items = []
                for item in data[:50]:
                    if isinstance(item, (dict, list)):
                        items.append(self._format_data_html(item, depth + 1))
                    else:
                        items.append(f"<span class='tag'>{self._escape(str(item)[:200])}</span>")
                result = " ".join(items)
                if len(data) > 50:
                    result += f"<p style='color:#9ca3af;margin-top:5px;'>... and {len(data) - 50} more</p>"
                return result

        elif data:
            return f"<pre>{self._escape(str(data)[:2000])}</pre>"
        return ""

    def _escape(self, text: str) -> str:
        """Escape HTML entities."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;")
        )
