"""
OmniSight AI - OSINT Modules Package
All 20+ intelligence-gathering modules organized as a unified framework.
"""

from .base import OSINTModule, ModuleResult

# New modules (10)
from .social_media import SocialMediaIntel
from .dark_web import DarkWebIntel
from .crypto_tracing import CryptoTracing
from .breach_intel import BreachIntel
from .shodan_intel import ShodanIntel
from .reverse_image import ReverseImageIntel
from .metadata_extract import MetadataExtract
from .threat_intel import ThreatIntel
from .ssl_analysis import SSLAnalysis
from .technology_stack import TechnologyStack
from .ai_analysis import GroqAIAnalysis

__all__ = [
    "OSINTModule",
    "ModuleResult",
    "SocialMediaIntel",
    "DarkWebIntel",
    "CryptoTracing",
    "BreachIntel",
    "ShodanIntel",
    "ReverseImageIntel",
    "MetadataExtract",
    "ThreatIntel",
    "SSLAnalysis",
    "TechnologyStack",
    "GroqAIAnalysis",
]
