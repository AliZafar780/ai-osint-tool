"""
Output caching module for OmniSight AI.
Prevents redundant lookups and speeds up repeated scans.
"""

import time
import hashlib
import json
import os
import threading
from typing import Any, Dict, Optional, Tuple


class MemoryCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self, ttl_seconds: int = 3600):
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._ttl = ttl_seconds
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key in self._cache:
                expires, value = self._cache[key]
                if time.time() < expires:
                    return value
                del self._cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            expire = time.time() + (ttl if ttl is not None else self._ttl)
            self._cache[key] = (expire, value)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
        return False

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()

    def cleanup(self) -> int:
        """Remove expired entries. Returns count removed."""
        now = time.time()
        with self._lock:
            expired = [k for k, (exp, _) in self._cache.items() if now >= exp]
            for k in expired:
                del self._cache[k]
        return len(expired)

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._cache)


class DiskCache:
    """Simple file-based cache with TTL."""

    def __init__(self, cache_dir: str = None, ttl_seconds: int = 3600):
        self._ttl = ttl_seconds
        self._cache_dir = cache_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".cache",
        )
        os.makedirs(self._cache_dir, exist_ok=True)

    def _key_path(self, key: str) -> str:
        hashed = hashlib.sha256(key.encode()).hexdigest()
        return os.path.join(self._cache_dir, f"{hashed}.json")

    def get(self, key: str) -> Optional[Any]:
        path = self._key_path(key)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if time.time() < data.get("_expires", 0):
                return data.get("value")
            os.remove(path)
        except (OSError, json.JSONDecodeError):
            pass
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        path = self._key_path(key)
        expire = time.time() + (ttl if ttl is not None else self._ttl)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"_expires": expire, "value": value}, f, default=str)
        except OSError:
            pass

    def clear(self) -> None:
        for fname in os.listdir(self._cache_dir):
            if fname.endswith(".json"):
                try:
                    os.remove(os.path.join(self._cache_dir, fname))
                except OSError:
                    pass


def get_cache(config: Optional[dict] = None) -> MemoryCache:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = MemoryCache()
    return _global_cache


_global_cache: Optional[MemoryCache] = None


def cached(key: str, ttl: Optional[int] = None):
    """Decorator to cache function results."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache = get_cache()
            cache_key = f"{func.__name__}:{key}:{hash(str(args))}:{hash(str(kwargs))}"
            result = cache.get(cache_key)
            if result is not None:
                return result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        return wrapper
    return decorator
