"""
OSINT Module Base Class
Provides standardized result format, error handling, and logging for all modules.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import json
import logging

logger = logging.getLogger("omnisight")


class ModuleResult:
    """Standardized result container for all OSINT modules."""

    def __init__(
        self,
        module_name: str,
        status: str = "completed",
        data: Any = None,
        error: Optional[str] = None,
        duration_ms: Optional[float] = None,
    ):
        self.module_name = module_name
        self.status = status  # completed, partial, failed, skipped
        self.data = data if data is not None else {}
        self.error = error
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.duration_ms = duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module": self.module_name,
            "status": self.status,
            "data": self.data,
            "error": self.error,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, default=str)

    def __bool__(self) -> bool:
        return self.status == "completed" and self.error is None

    def __repr__(self) -> str:
        return f"<ModuleResult {self.module_name}: {self.status}>"


class OSINTModule:
    """Base class for all OSINT intelligence modules."""

    name: str = "base"
    description: str = "Base OSINT module"
    requires_api_key: bool = False
    api_key_name: Optional[str] = None

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.logger = logger

    def execute(self, target: str, **kwargs) -> ModuleResult:
        """Execute the module against a target. Override in subclass."""
        raise NotImplementedError("Subclasses must implement execute()")

    def _success(self, data: Any, duration_ms: Optional[float] = None) -> ModuleResult:
        return ModuleResult(
            module_name=self.name,
            status="completed",
            data=data,
            duration_ms=duration_ms,
        )

    def _partial(self, data: Any, error: str) -> ModuleResult:
        return ModuleResult(
            module_name=self.name,
            status="partial",
            data=data,
            error=error,
        )

    def _failed(self, error: str) -> ModuleResult:
        return ModuleResult(
            module_name=self.name,
            status="failed",
            error=error,
        )

    def _skipped(self, reason: str = "Module skipped") -> ModuleResult:
        return ModuleResult(
            module_name=self.name,
            status="skipped",
            error=reason,
        )

    def get_info(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "requires_api_key": self.requires_api_key,
            "api_key_name": self.api_key_name,
        }
