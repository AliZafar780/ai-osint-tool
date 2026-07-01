"""
OmniSight AI Web Dashboard
FastAPI-based web interface for running OSINT scans and viewing reports.
"""

import os
import sys
import json
import time
import threading
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastapi import FastAPI, HTTPException, Query, Request, BackgroundTasks
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from modules import (
    SocialMediaIntel, DarkWebIntel, CryptoTracing, BreachIntel,
    ShodanIntel, ReverseImageIntel, MetadataExtract, ThreatIntel,
    SSLAnalysis, TechnologyStack, GroqAIAnalysis,
)
from utils.cache import get_cache
from utils.config import load_config
from reports.json_report import JSONReportGenerator
from reports.markdown_report import MarkdownReportGenerator
from reports.html_report import HTMLReportGenerator


class ScanRequest(BaseModel):
    """API scan request model."""
    target: str
    modules: Optional[List[str]] = None
    analysis_type: Optional[str] = "full"
    output_formats: Optional[List[str]] = None


class DashboardApp:
    """OmniSight AI Web Dashboard."""

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or load_config()
        self.cache = get_cache()
        self.scan_history: List[Dict] = []
        self.active_scans: Dict[str, threading.Thread] = {}

        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI is required for the web dashboard. "
                "Install with: pip install fastapi uvicorn"
            )

        self.app = FastAPI(
            title="OmniSight AI Dashboard",
            description="Advanced OSINT with AI Integration - Web Interface",
            version="2.0.0",
        )

        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._register_routes()

    def _register_routes(self):
        """Register all API and web routes."""

        @self.app.get("/", response_class=HTMLResponse)
        async def index():
            return self._render_dashboard()

        @self.app.get("/api/health")
        async def health():
            return {
                "status": "ok",
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "fastapi": True,
                "modules_loaded": self._count_modules(),
            }

        @self.app.get("/api/modules")
        async def list_modules():
            return self._get_module_list()

        @self.app.post("/api/scan")
        async def run_scan(request: ScanRequest, background_tasks: BackgroundTasks):
            scan_id = f"scan_{int(time.time())}_{request.target[:30]}"
            
            # Validate target
            if not request.target or len(request.target.strip()) < 2:
                raise HTTPException(status_code=400, detail="Invalid target")

            # Start scan in background
            background_tasks.add_task(
                self._execute_scan, scan_id, request
            )

            return {
                "scan_id": scan_id,
                "target": request.target,
                "status": "started",
                "modules": request.modules or "all",
            }

        @self.app.get("/api/scan/{scan_id}")
        async def get_scan_status(scan_id: str):
            for scan in self.scan_history:
                if scan.get("scan_id") == scan_id:
                    return scan
            raise HTTPException(status_code=404, detail="Scan not found")

        @self.app.get("/api/scan/{scan_id}/report/{fmt}")
        async def get_report(scan_id: str, fmt: str = "json"):
            if fmt not in ("json", "markdown", "html"):
                raise HTTPException(status_code=400, detail="Unsupported format")

            for scan in self.scan_history:
                if scan.get("scan_id") == scan_id:
                    if scan.get("status") != "completed":
                        raise HTTPException(status_code=400, detail="Scan not completed")

                    results = scan.get("results", {})
                    target = scan.get("target", "unknown")

                    if fmt == "json":
                        gen = JSONReportGenerator()
                    elif fmt == "markdown":
                        gen = MarkdownReportGenerator()
                    else:
                        gen = HTMLReportGenerator()

                    filepath = gen.generate(target, results)
                    return FileResponse(
                        filepath,
                        media_type="application/octet-stream",
                        filename=os.path.basename(filepath),
                    )

            raise HTTPException(status_code=404, detail="Scan not found")

        @self.app.get("/api/history")
        async def get_history(limit: int = Query(10, ge=1, le=100)):
            return self.scan_history[-limit:]

        @self.app.get("/api/cache/stats")
        async def cache_stats():
            return {
                "cache_size": self.cache.size if hasattr(self.cache, "size") else "unknown",
                "type": type(self.cache).__name__,
            }

    def _render_dashboard(self) -> str:
        """Render the main dashboard HTML."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniSight AI - Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0e17;
            color: #e0e0e0;
            min-height: 100vh;
        }}
        .navbar {{
            background: linear-gradient(135deg, #00d4ff 0%, #0072ff 50%);
            padding: 16px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .navbar h1 {{ color: white; font-size: 1.4rem; }}
        .navbar .version {{ color: rgba(255,255,255,0.7); font-size: 0.8rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
        .card {{
            background: #111827;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
        }}
        .card h2 {{ color: #00d4ff; margin-bottom: 16px; font-size: 1.2rem; }}
        .input-group {{ display: flex; gap: 12px; flex-wrap: wrap; }}
        .input-group input {{
            flex: 1;
            min-width: 200px;
            padding: 12px 16px;
            background: #1a2332;
            border: 1px solid #1e293b;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
        }}
        .input-group input:focus {{ outline: none; border-color: #00d4ff; }}
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }}
        .btn-primary {{ background: #00d4ff; color: #0a0e17; }}
        .btn-primary:hover {{ background: #00b4d9; transform: translateY(-1px); }}
        .btn-secondary {{ background: #1e293b; color: #e0e0e0; }}
        .btn-secondary:hover {{ background: #2d3a4e; }}
        .btn-danger {{ background: #dc2626; color: white; }}
        .btn-danger:hover {{ background: #b91c1c; }}
        .module-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 12px;
            margin: 16px 0;
        }}
        .module-item {{
            background: #1a2332;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #1e293b;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .module-item input[type="checkbox"] {{ width: 18px; height: 18px; accent-color: #00d4ff; }}
        .module-item label {{ flex: 1; cursor: pointer; }}
        .module-item .mod-name {{ color: #00d4ff; font-weight: 500; }}
        .module-item .mod-desc {{ color: #9ca3af; font-size: 0.8rem; display: block; }}
        .results {{
            background: #1a2332;
            padding: 16px;
            border-radius: 8px;
            max-height: 400px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85rem;
            white-space: pre-wrap;
        }}
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .status-running {{ background: #1e3a5f; color: #93c5fd; }}
        .status-completed {{ background: #065f46; color: #6ee7b7; }}
        .status-failed {{ background: #7f1d1d; color: #fca5a5; }}
        .history-item {{
            padding: 12px;
            border-bottom: 1px solid #1e293b;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .history-item:last-child {{ border-bottom: none; }}
        .output-formats {{ display: flex; gap: 8px; margin: 12px 0; flex-wrap: wrap; }}
        .format-btn {{
            padding: 6px 14px;
            border: 1px solid #1e293b;
            border-radius: 6px;
            background: #1a2332;
            color: #e0e0e0;
            cursor: pointer;
            font-size: 0.85rem;
        }}
        .format-btn.active {{ border-color: #00d4ff; background: #0a3a5f; color: #00d4ff; }}
        .format-btn:hover {{ border-color: #00d4ff; }}
        .loader {{
            width: 40px;
            height: 40px;
            border: 3px solid #1e293b;
            border-top: 3px solid #00d4ff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .form-row {{ margin: 12px 0; }}
        .form-row label {{ display: block; color: #9ca3af; margin-bottom: 4px; font-size: 0.9rem; }}
        .form-row select {{
            padding: 10px 14px;
            background: #1a2332;
            border: 1px solid #1e293b;
            border-radius: 8px;
            color: white;
            width: 100%;
            font-size: 0.95rem;
        }}
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #111827; }}
        ::-webkit-scrollbar-thumb {{ background: #1e293b; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #374151; }}
    </style>
</head>
<body>
    <nav class="navbar">
        <div>
            <h1>OmniSight AI Dashboard</h1>
            <span class="version">v2.0.0 — Advanced OSINT with AI</span>
        </div>
        <div>
            <button class="btn btn-secondary" onclick="refreshHistory()">Refresh</button>
        </div>
    </nav>

    <div class="container">
        <!-- Scan Input -->
        <div class="card">
            <h2>New Scan</h2>
            <div class="input-group">
                <input type="text" id="targetInput" placeholder="Enter target (domain, IP, email, URL...)" />
                <button class="btn btn-primary" onclick="startScan()">Start Scan</button>
            </div>

            <div class="form-row" style="margin-top:16px;">
                <label>Analysis Type (with AI key)</label>
                <select id="analysisType">
                    <option value="full">Full Security Assessment</option>
                    <option value="quick">Quick Overview</option>
                    <option value="vulnerability">Vulnerability Focus</option>
                    <option value="remediation">Remediation Focus</option>
                    <option value="compliance">Compliance Check</option>
                </select>
            </div>

            <div style="margin-top:16px;">
                <label style="color:#9ca3af;font-size:0.9rem;">Output Formats:</label>
                <div class="output-formats">
                    <button class="format-btn active" data-format="json" onclick="toggleFormat(this)">JSON</button>
                    <button class="format-btn active" data-format="markdown" onclick="toggleFormat(this)">Markdown</button>
                    <button class="format-btn active" data-format="html" onclick="toggleFormat(this)">HTML</button>
                </div>
            </div>

            <details style="margin-top:16px;">
                <summary style="color:#00d4ff;cursor:pointer;">Select Modules (default: all)</summary>
                <div class="module-grid" id="moduleGrid"></div>
            </details>
        </div>

        <!-- Status -->
        <div class="card" id="statusCard" style="display:none;">
            <h2>Scan Status</h2>
            <div id="scanStatus"></div>
            <div id="scanResults" class="results"></div>
        </div>

        <!-- History -->
        <div class="card">
            <h2>Scan History</h2>
            <div id="historyList">
                <p style="color:#6b7280;">No scans yet. Start your first scan above.</p>
            </div>
        </div>
    </div>

    <script>
        const API = '/api';
        let selectedFormats = ['json', 'markdown', 'html'];
        let activeModules = [];

        function toggleFormat(btn) {{
            btn.classList.toggle('active');
            const fmt = btn.dataset.format;
            if (selectedFormats.includes(fmt)) {{
                selectedFormats = selectedFormats.filter(f => f !== fmt);
            }} else {{
                selectedFormats.push(fmt);
            }}
        }}

        function loadModules() {{
            fetch(API + '/modules')
                .then(r => r.json())
                .then(modules => {{
                    const grid = document.getElementById('moduleGrid');
                    grid.innerHTML = Object.entries(modules).map(([key, mod]) => `
                        <div class="module-item">
                            <input type="checkbox" id="mod-${{key}}" checked onchange="toggleModule('${{key}}')">
                            <label for="mod-${{key}}">
                                <span class="mod-name">${{mod.name || key}}</span>
                                <span class="mod-desc">${{mod.description || ''}}</span>
                            </label>
                        </div>
                    `).join('');
                    activeModules = Object.keys(modules);
                }});
        }}

        function toggleModule(name) {{
            if (activeModules.includes(name)) {{
                activeModules = activeModules.filter(m => m !== name);
            }} else {{
                activeModules.push(name);
            }}
        }}

        function startScan() {{
            const target = document.getElementById('targetInput').value.trim();
            if (!target) {{ alert('Please enter a target'); return; }}

            const card = document.getElementById('statusCard');
            card.style.display = 'block';
            document.getElementById('scanStatus').innerHTML = '<span class="status-badge status-running">Running</span>';
            document.getElementById('scanResults').textContent = 'Starting scan...';

            fetch(API + '/scan', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify({{
                    target: target,
                    modules: activeModules.length > 0 ? activeModules : null,
                    analysis_type: document.getElementById('analysisType').value,
                    output_formats: selectedFormats,
                }})
            }})
            .then(r => r.json())
            .then(data => {{
                pollScan(data.scan_id);
            }})
            .catch(err => {{
                document.getElementById('scanResults').textContent = 'Error: ' + err;
            }});
        }}

        function pollScan(scanId) {{
            const interval = setInterval(() => {{
                fetch(API + '/scan/' + scanId)
                    .then(r => r.json())
                    .then(data => {{
                        const statusEl = document.getElementById('scanStatus');
                        const resultsEl = document.getElementById('scanResults');

                        statusEl.innerHTML = '<span class="status-badge status-' + data.status + '">' + data.status + '</span>';

                        if (data.status === 'completed') {{
                            clearInterval(interval);
                            resultsEl.textContent = JSON.stringify(data.results || data, null, 2);
                            refreshHistory();
                        }} else if (data.status === 'failed') {{
                            clearInterval(interval);
                            resultsEl.textContent = 'Scan failed: ' + (data.error || 'Unknown error');
                        }} else {{
                            resultsEl.textContent = 'Scanning... (' + (data.progress || 'in progress') + ')';
                        }}
                    }});
            }}, 2000);
        }}

        function refreshHistory() {{
            fetch(API + '/history?limit=20')
                .then(r => r.json())
                .then(history => {{
                    const list = document.getElementById('historyList');
                    if (history.length === 0) {{
                        list.innerHTML = '<p style="color:#6b7280;">No scans yet.</p>';
                        return;
                    }}
                    list.innerHTML = history.reverse().map(h => `
                        <div class="history-item">
                            <div>
                                <strong style="color:#00d4ff;">${{h.target}}</strong>
                                <span style="color:#9ca3af;font-size:0.85rem;margin-left:8px;">
                                    ${{new Date(h.timestamp).toLocaleString()}}
                                </span>
                            </div>
                            <div>
                                <span class="status-badge status-${{h.status}}">${{h.status}}</span>
                                <button class="btn btn-secondary" style="padding:4px 12px;margin-left:8px;font-size:0.8rem;"
                                    onclick='viewScan(${{JSON.stringify(h).replace(/'/g, "&#39;")}})'>View</button>
                            </div>
                        </div>
                    `).join('');
                }});
        }}

        function viewScan(scan) {{
            const card = document.getElementById('statusCard');
            card.style.display = 'block';
            document.getElementById('scanStatus').innerHTML = 
                '<span class="status-badge status-' + scan.status + '">' + scan.status + '</span>' +
                '<span style="margin-left:12px;color:#9ca3af;">' + scan.target + '</span>';
            document.getElementById('scanResults').textContent = JSON.stringify(scan.results || scan, null, 2);
        }}

        loadModules();
        refreshHistory();
        setInterval(refreshHistory, 10000);
    </script>
</body>
</html>"""

    def _count_modules(self) -> int:
        """Count available modules."""
        return len(self._get_module_list())

    def _get_module_list(self) -> Dict:
        """Get list of available modules with descriptions."""
        return {
            "social_media": {"name": "Social Media", "description": "Profile discovery across 20+ platforms", "requires_key": False},
            "dark_web": {"name": "Dark Web", "description": "Paste monitoring, onion search, leak detection", "requires_key": False},
            "crypto_tracing": {"name": "Crypto Tracing", "description": "BTC/ETH transaction analysis", "requires_key": False},
            "breach_intel": {"name": "Breach Intel", "description": "Credential leak and breach checking", "requires_key": False},
            "shodan_intel": {"name": "Shodan/Censys", "description": "Internet device intelligence", "requires_key": True},
            "reverse_image": {"name": "Reverse Image", "description": "Image search across engines", "requires_key": False},
            "metadata_extract": {"name": "Metadata", "description": "Document EXIF and properties", "requires_key": False},
            "threat_intel": {"name": "Threat Intel", "description": "Multi-source reputation and IoCs", "requires_key": False},
            "ssl_analysis": {"name": "SSL/TLS", "description": "Certificate and protocol analysis", "requires_key": False},
            "technology_stack": {"name": "Tech Stack", "description": "Framework and platform detection", "requires_key": False},
            "ai_analysis": {"name": "AI Analysis", "description": "Groq-powered security assessment", "requires_key": True},
        }

    def _execute_scan(self, scan_id: str, request: ScanRequest):
        """Execute a scan with selected modules."""
        results = {}
        target = request.target.strip()
        modules_to_run = request.modules

        all_modules = {
            "social_media": SocialMediaIntel(self.config),
            "dark_web": DarkWebIntel(self.config),
            "crypto_tracing": CryptoTracing(self.config),
            "breach_intel": BreachIntel(self.config),
            "shodan_intel": ShodanIntel(self.config),
            "reverse_image": ReverseImageIntel(self.config),
            "metadata_extract": MetadataExtract(self.config),
            "threat_intel": ThreatIntel(self.config),
            "ssl_analysis": SSLAnalysis(self.config),
            "technology_stack": TechnologyStack(self.config),
            "ai_analysis": GroqAIAnalysis(self.config),
        }

        scan_entry = {
            "scan_id": scan_id,
            "target": target,
            "status": "running",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "progress": 0,
            "results": {},
        }
        self.scan_history.append(scan_entry)

        try:
            total = len(modules_to_run) if modules_to_run else len(all_modules)
            completed = 0

            for mod_name, mod_instance in all_modules.items():
                if modules_to_run and mod_name not in modules_to_run:
                    continue

                try:
                    if mod_name == "ai_analysis":
                        result = mod_instance.execute(
                            target,
                            analysis_type=request.analysis_type or "full",
                            scan_results=results,
                        )
                    else:
                        result = mod_instance.execute(target)

                    results[mod_name] = result.to_dict() if hasattr(result, "to_dict") else {"data": str(result)}
                except Exception as e:
                    results[mod_name] = {"status": "failed", "error": str(e)[:200]}

                completed += 1
                scan_entry["progress"] = int((completed / total) * 100)

            scan_entry["status"] = "completed"
            scan_entry["results"] = results

            # Generate reports if formats specified
            if request.output_formats:
                for fmt in request.output_formats:
                    try:
                        if fmt == "json":
                            gen = JSONReportGenerator()
                        elif fmt == "markdown":
                            gen = MarkdownReportGenerator()
                        elif fmt == "html":
                            gen = HTMLReportGenerator()
                        else:
                            continue
                        filepath = gen.generate(target, results)
                        scan_entry.setdefault("reports", {})[fmt] = filepath
                    except Exception as e:
                        print(f"Report generation failed ({fmt}): {e}")

        except Exception as e:
            scan_entry["status"] = "failed"
            scan_entry["error"] = str(e)[:500]
            scan_entry["results"] = results

    def run(self, host: str = "127.0.0.1", port: int = 8080, debug: bool = False):
        """Run the dashboard server."""
        import uvicorn
        print(f"  OmniSight AI Dashboard running at: http://{host}:{port}")
        print(f"  API available at: http://{host}:{port}/api/")
        uvicorn.run(self.app, host=host, port=port, log_level="info" if debug else "warning")


def create_app(config: Optional[Dict] = None):
    """Factory function to create dashboard app."""
    dash = DashboardApp(config)
    return dash.app


def run_dashboard(config: Optional[Dict] = None):
    """Run the dashboard directly."""
    dash = DashboardApp(config)
    dash_config = (config or {}).get("dashboard", {})
    dash.run(
        host=dash_config.get("host", "127.0.0.1"),
        port=dash_config.get("port", 8080),
        debug=dash_config.get("debug", False),
    )


if __name__ == "__main__":
    run_dashboard()
