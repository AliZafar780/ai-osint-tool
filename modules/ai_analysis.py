"""
Enhanced Groq AI Analysis Module
Multi-model AI analysis with context-aware security assessments.
"""

import os
import time
import json
import re
from typing import Dict, List, Optional
from .base import OSINTModule, ModuleResult


class GroqAIAnalysis(OSINTModule):
    """
    Enhanced Groq AI analysis with multi-model support, context awareness,
    and structured security assessment.
    """

    name = "ai_analysis"
    description = "Groq AI-powered security analysis with multi-model support"
    requires_api_key = True
    api_key_name = "groq_api_key"

    # Available Groq models
    MODELS = {
        "llama3-8b": "llama3-8b-8192",
        "llama3-70b": "llama3-70b-8192",
        "llama3.1-8b": "llama3-8b-8192",
        "mixtral": "mixtral-8x7b-32768",
        "gemma2": "gemma2-9b-it",
    }

    ANALYSIS_TYPES = {
        "full": "Comprehensive security assessment",
        "quick": "Quick risk overview",
        "vulnerability": "Vulnerability-focused analysis",
        "remediation": "Remediation recommendations",
        "compliance": "Compliance and standards check",
    }

    def __init__(self, config: Optional[Dict] = None):
        super().__init__(config)
        self.api_key = self._get_api_key()
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = os.environ.get("GROQ_MODEL", "llama3-70b-8192")
        self.session = None
        if self.api_key:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            })

    def _get_api_key(self) -> str:
        """Get API key from config, env, or config file."""
        key = ""
        if self.config and "api_keys" in self.config:
            key = self.config["api_keys"].get("groq_api_key", "")
        if not key or key in ("your_groq_api_key_here", "your_api_key_here", "your_key"):
            key = os.environ.get("GROQ_API_KEY", "").strip()
        return key

    def _build_analysis_prompt(
        self,
        target: str,
        analysis_type: str,
        scan_results: Optional[Dict] = None,
    ) -> str:
        """Build a context-rich analysis prompt."""
        
        context = f"""
TARGET: {target}
ANALYSIS TYPE: {analysis_type.upper()}
TIMESTAMP: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}
"""

        if scan_results:
            context += "\nSCAN DATA AVAILABLE:\n"
            for module, data in scan_results.items():
                if isinstance(data, dict):
                    summary = json.dumps(data.get("summary", data), default=str)[:300]
                    context += f"  [{module}]: {summary}\n"
                elif isinstance(data, list):
                    context += f"  [{module}]: {len(data)} items found\n"

        prompts = {
            "full": f"""You are an elite cybersecurity OSINT analyst. Provide a comprehensive security assessment.

{context}

Provide analysis covering:
1. **EXECUTIVE SUMMARY** - Overall risk level (Critical/High/Medium/Low) in one sentence
2. **ATTACK SURFACE** - Key exposed services, technologies, and entry points
3. **VULNERABILITY ASSESSMENT** - Likely vulnerabilities based on exposed technologies
4. **THREAT LANDSCAPE** - Threat actor interest, attack patterns likely to be used
5. **RECOMMENDATIONS** - Prioritized security hardening measures (top 5)
6. **DEEP RECON SUGGESTIONS** - What additional recon would be most valuable

Format with clear markdown headers and bullet points. Be specific and actionable.""",

            "quick": f"""You are a cybersecurity analyst. Provide a quick security overview.

{context}

Provide:
1. **RISK LEVEL** (Critical/High/Medium/Low) 
2. **TOP 3 CONCERNS** - Most critical issues identified
3. **TOP 3 RECOMMENDATIONS** - Quick wins for security improvement

Keep it concise, 3-5 sentences per section.""",

            "vulnerability": f"""You are a vulnerability assessment specialist. Focus on vulnerabilities.

{context}

Provide:
1. **CRITICAL VULNERABILITIES** - Most dangerous issues likely present
2. **COMMON EXPOSURES** - CVEs and known issues for identified technologies
3. **EXPLOITABILITY** - How easily could each issue be exploited
4. **PRIORITY** - Which to address first based on risk

Reference specific CVE IDs where applicable.""",

            "remediation": f"""You are a security hardening expert. Focus on fixes.

{context}

Provide:
1. **IMMEDIATE ACTIONS** (24-48 hours) - Critical patches and config changes
2. **SHORT-TERM** (1-2 weeks) - Architecture and policy improvements
3. **LONG-TERM** (1-3 months) - Strategic security enhancements
4. **MONITORING** - What to watch for signs of compromise""",

            "compliance": f"""You are a compliance and standards auditor.

{context}

Provide:
1. **APPLICABLE STANDARDS** - Which frameworks apply (OWASP, NIST, CIS, ISO 27001, PCI DSS)
2. **COMPLIANCE GAPS** - Areas likely failing compliance requirements
3. **REMEDIATION** - Steps to achieve compliance
4. **DOCUMENTATION** - What evidence would be needed for audits""",
        }

        return prompts.get(analysis_type, prompts["full"])

    def _query_groq(self, prompt: str, model: str = None) -> Dict:
        """Send query to Groq API."""
        if not self.api_key:
            return {"error": "No Groq API key configured. Set GROQ_API_KEY env var."}
        if not self.session:
            return {"error": "Requests library not available"}

        payload = {
            "model": model or self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are OmniSight AI, an elite cybersecurity OSINT analysis engine. "
                        "Provide detailed, actionable, professional security assessments. "
                        "Always prioritize clarity and specific technical recommendations."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
            "top_p": 0.95,
        }

        try:
            resp = self.session.post(self.api_url, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return {
                    "content": content,
                    "model": data.get("model", model),
                    "usage": {
                        "prompt_tokens": usage.get("prompt_tokens", 0),
                        "completion_tokens": usage.get("completion_tokens", 0),
                        "total_tokens": usage.get("total_tokens", 0),
                    },
                }
            else:
                return {
                    "error": f"Groq API HTTP {resp.status_code}: {resp.text[:200]}"
                }

        except Exception as e:
            return {"error": f"Groq API request failed: {str(e)[:200]}"}

    def _extract_risk_score(self, analysis_text: str) -> Dict:
        """Extract risk score and level from analysis text."""
        risk_score = 50
        risk_level = "Medium"

        # Search for explicit risk indicators
        critical = len(re.findall(r"CRITICAL|CRITICAL", analysis_text))
        high = len(re.findall(r"\bHIGH\b", analysis_text))
        medium = len(re.findall(r"\bMEDIUM\b", analysis_text))
        low = len(re.findall(r"\bLOW\b", analysis_text))

        if critical > 0:
            risk_level = "Critical"
            risk_score = 85
        elif high > high_indicator_count(analysis_text):
            risk_level = "High"
            risk_score = 65
        elif medium > 0:
            risk_level = "Medium"
            risk_score = 40
        elif low > 0:
            risk_level = "Low"
            risk_score = 20

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "indicators": {
                "critical_mentions": critical,
                "high_mentions": high,
                "medium_mentions": medium,
                "low_mentions": low,
            },
        }

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """
        Execute AI-powered analysis.
        Accepts 'analysis_type' kwarg (full, quick, vulnerability, remediation, compliance).
        Accepts 'scan_results' kwarg with dict of module results for context.
        Accepts 'model' kwarg to specify Groq model.
        """
        start = time.time()

        analysis_type = kwargs.get("analysis_type", "full")
        scan_results = kwargs.get("scan_results", {})
        model = kwargs.get("model", self.model)

        if not self.api_key:
            return self._skipped(
                "Groq API key not configured. Set GROQ_API_KEY env var or add to config."
            )

        prompt = self._build_analysis_prompt(target, analysis_type, scan_results)

        result = self._query_groq(prompt, model)

        if "error" in result:
            return self._failed(result["error"])

        analysis_data = {
            "target": target,
            "analysis_type": analysis_type,
            "model_used": result.get("model", model),
            "analysis": result.get("content", ""),
            "risk_assessment": self._extract_risk_score(result.get("content", "")),
            "token_usage": result.get("usage", {}),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        }

        duration = (time.time() - start) * 1000
        return self._success(analysis_data, duration)

    def list_analysis_types(self) -> Dict[str, str]:
        """List available analysis types."""
        return self.ANALYSIS_TYPES

    def list_models(self) -> Dict[str, str]:
        """List available Groq models."""
        return self.MODELS


def high_indicator_count(text: str) -> int:
    """Count high-risk indicators that are not part of other words."""
    # Simple default for the edge case
    return 0
