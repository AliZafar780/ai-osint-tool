#!/usr/bin/env python3
"""
OmniSight AI v2.0 - Advanced OSINT Tool with Groq AI Integration
Author: Ali Zafar (alizafarbati)
Version: 2.0.0 - 10 new modules, web dashboard, multi-format reports, caching

A modular, multi-threaded Open-Source Intelligence (OSINT) tool with 20+ modules
covering social media, dark web, crypto, breach intel, Shodan/Censys, and more.
"""

import os
import sys
import time
import json
import argparse
import re
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import init, Fore, Style

from utils.config import load_config
from utils.cache import get_cache
from utils.concurrent import ThreadPool, ProgressTracker
from modules import (
    SocialMediaIntel, DarkWebIntel, CryptoTracing, BreachIntel,
    ShodanIntel, ReverseImageIntel, MetadataExtract, ThreatIntel,
    SSLAnalysis, TechnologyStack, GroqAIAnalysis,
    OSINTModule, ModuleResult,
)
from reports.json_report import JSONReportGenerator
from reports.markdown_report import MarkdownReportGenerator
from reports.html_report import HTMLReportGenerator

init()

# Color scheme
class Colors:
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Style.RESET_ALL
    BRIGHT = Style.BRIGHT


def print_banner():
    """Display the OmniSight AI banner."""
    banner = f"""
{Colors.CYAN}{Colors.BRIGHT}
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   ██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ ██╗     ██╗ ██████╗ ║
║   ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗║
║   ██████╔╝██║   ██║██████╔╝   ██║   █████╗  ██║   ██║██║     ██║██║   ██║║
║   ██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══╝  ██║   ██║██║     ██║██║   ██║║
║   ██║     ╚██████╔╝██║  ██║   ██║   ██║     ╚██████╔╝███████╗██║╚██████╔╝║
║   ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚═════╝ ║
║                                                                      ║
║   OmniSight AI v2.0                                           ║
║   20+ OSINT Modules | AI-Powered | Web Dashboard                           ║
║   Author: Ali Zafar (@alizafarbati)                                      ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
{Colors.RESET}
    """
    print(banner)


class OmniSightEngine:
    """Main OSINT engine orchestrating all modules."""

    def __init__(self, target: str, config: Optional[Dict] = None):
        self.target = target.strip()
        self.config = config or load_config()
        self.cache = get_cache()
        self.results: Dict[str, Any] = {}
        self.progress = ProgressTracker()

    def log(self, message: str, level: str = "INFO"):
        """Print timestamped, color-coded log message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "INFO": Colors.BLUE,
            "SECTION": Colors.CYAN,
        }
        color = color_map.get(level, Colors.WHITE)
        level_str = f"[{level:<7}]"
        print(f"  {color}{level_str} {message}{Colors.RESET}")

    def _run_module(self, name: str, module: OSINTModule, **kwargs) -> ModuleResult:
        """Run a single module with timing and error handling."""
        self.log(f"Starting {name}...", "INFO")
        self.progress.start_task(name)

        start = time.time()
        try:
            result = module.execute(self.target, **kwargs)
            duration = (time.time() - start) * 1000
            if isinstance(result, ModuleResult):
                result.duration_ms = duration

            if result and result.status == "completed":
                self.log(f"{name}: Completed ({duration:.0f}ms)", "SUCCESS")
            elif result and result.status == "partial":
                self.log(f"{name}: Partial ({duration:.0f}ms) - {result.error}", "WARNING")
            else:
                self.log(f"{name}: {result.status} - {result.error}", "WARNING")

            self.progress.complete_task(name)
            return result

        except Exception as e:
            duration = (time.time() - start) * 1000
            self.log(f"{name}: Failed - {e}", "ERROR")
            self.progress.fail_task(name, str(e))
            return ModuleResult(name, status="failed", error=str(e)[:200], duration_ms=duration)

    def run_all_modules(self, modules_to_run: Optional[List[str]] = None):
        """Run selected modules (or all) against the target."""
        print_banner()
        print(f"\n{Colors.BRIGHT}Target: {Colors.CYAN}{self.target}{Colors.RESET}")
        print(f"{'='*60}\n")

        all_modules: Dict[str, OSINTModule] = {
            "Social Media Intel": SocialMediaIntel(self.config),
            "Dark Web Intel": DarkWebIntel(self.config),
            "Crypto Tracing": CryptoTracing(self.config),
            "Breach Intel": BreachIntel(self.config),
            "Shodan/Censys Intel": ShodanIntel(self.config),
            "Reverse Image Search": ReverseImageIntel(self.config),
            "Metadata Extraction": MetadataExtract(self.config),
            "Threat Intelligence": ThreatIntel(self.config),
            "SSL/TLS Analysis": SSLAnalysis(self.config),
            "Tech Stack Fingerprinting": TechnologyStack(self.config),
            "AI Security Analysis": GroqAIAnalysis(self.config),
        }

        # Filter modules
        if modules_to_run:
            selected = {}
            for mod_name, mod_instance in all_modules.items():
                mod_key = mod_name.lower().replace(" ", "_").replace("/", "_")
                if any(run_key.lower() in mod_name.lower() or run_key.lower() in mod_key for run_key in modules_to_run):
                    selected[mod_name] = mod_instance
            if not selected:
                self.log("No matching modules found. Running all.", "WARNING")
                selected = all_modules
        else:
            selected = all_modules

        # Setup progress
        for name in selected:
            self.progress.add_task(name)

        # Run modules sequentially (some have rate limits)
        for name, module in selected.items():
            kwargs = {}
            if isinstance(module, GroqAIAnalysis):
                kwargs["scan_results"] = self.results
            result = self._run_module(name, module, **kwargs)
            self.results[name] = result.to_dict() if hasattr(result, 'to_dict') else {"data": str(result)}
            time.sleep(0.3)  # Brief pause between modules

        # Print summary
        print(f"\n{Colors.GREEN}{'='*60}")
        print(f"  Scan Complete!")
        print(f"  Target: {self.target}")
        print(f"  Modules: {self.progress.summary}")
        print(f"{'='*60}{Colors.RESET}")

        return self.results

    def generate_reports(self, formats: List[str] = None) -> Dict[str, str]:
        """Generate reports in specified formats."""
        if formats is None:
            formats = ["json", "markdown", "html"]

        generated = {}
        generators = {
            "json": JSONReportGenerator(),
            "markdown": MarkdownReportGenerator(),
            "html": HTMLReportGenerator(),
        }

        for fmt in formats:
            if fmt in generators:
                try:
                    filepath = generators[fmt].generate(self.target, self.results)
                    generated[fmt] = filepath
                    self.log(f"Report saved: {filepath}", "SUCCESS")
                except Exception as e:
                    self.log(f"Report generation failed ({fmt}): {e}", "ERROR")

        return generated


def main():
    """CLI entry point for OmniSight AI."""
    parser = argparse.ArgumentParser(
        description="OmniSight AI v2.0 - Advanced OSINT with 20+ Modules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s example.com
  %(prog)s example.com -m social_media,threat_intel
  %(prog)s example.com --format json,html --groq-key your_key
  %(prog)s example.com --dashboard
        """,
    )
    parser.add_argument("target", help="Target: domain, IP, email, username, or URL")
    parser.add_argument("-m", "--modules", help="Comma-separated modules to run (default: all)")
    parser.add_argument("-f", "--format", default="json,markdown,html", help="Report formats (comma-separated): json,markdown,html")
    parser.add_argument("--groq-key", help="Groq API key for AI analysis")
    parser.add_argument("--analysis-type", default="full", choices=["full", "quick", "vulnerability", "remediation", "compliance"], help="AI analysis depth")
    parser.add_argument("--dashboard", action="store_true", help="Launch web dashboard")
    parser.add_argument("--dashboard-port", type=int, default=8080, help="Dashboard port")
    parser.add_argument("--no-cache", action="store_true", help="Disable result caching")
    parser.add_argument("-o", "--output", help="Output directory for reports (default: ./osint_results)")

    args = parser.parse_args()

    # Load config
    config = load_config()

    # Override config with CLI args
    if args.groq_key:
        config["api_keys"]["groq_api_key"] = args.groq_key
    if args.output:
        config["output"]["directory"] = args.output
    if args.no_cache:
        config["cache"]["enabled"] = False

    # Launch dashboard
    if args.dashboard:
        try:
            from dashboard.app import DashboardApp
            dash = DashboardApp(config)
            dash_config = config.get("dashboard", {})
            print(f"\n{Colors.GREEN}Starting OmniSight AI Dashboard...{Colors.RESET}")
            dash.run(
                host=dash_config.get("host", "127.0.0.1"),
                port=args.dashboard_port,
                debug=dash_config.get("debug", False),
            )
        except ImportError as e:
            print(f"{Colors.RED}Dashboard requires FastAPI: pip install fastapi uvicorn{Colors.RESET}")
            sys.exit(1)
        return

    # Parse module filters
    modules_to_run = None
    if args.modules:
        modules_to_run = [m.strip() for m in args.modules.split(",")]

    # Parse output formats
    formats = [f.strip() for f in args.format.split(",") if f.strip()]

    # Run engine
    engine = OmniSightEngine(args.target, config)
    engine.run_all_modules(modules_to_run)

    # Generate reports
    report_files = engine.generate_reports(formats)

    # Print final summary
    print(f"\n{Colors.BRIGHT}{'='*60}")
    print(f"  OmniSight AI Scan Summary")
    print(f"{'='*60}{Colors.RESET}")
    for fmt, path in report_files.items():
        print(f"  {Colors.CYAN}{fmt.upper()}:{Colors.RESET} {path}")

    # Sync config to output directory
    output_dir = config["output"]["directory"]
    if os.path.isdir(output_dir):
        print(f"\n  Reports saved to: {Colors.GREEN}{os.path.abspath(output_dir)}{Colors.RESET}")

    print(f"\n{Colors.GREEN}Done.{Colors.RESET}\n")


if __name__ == "__main__":
    main()
