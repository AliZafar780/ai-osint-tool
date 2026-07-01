"""
Concurrent execution utilities for OmniSight AI.
Provides thread pool management and async helpers.
"""

import concurrent.futures
import threading
from typing import Any, Callable, Dict, List, Optional


class ThreadPool:
    """Thread pool for parallel OSINT module execution."""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self._executor: Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._futures: Dict[str, concurrent.futures.Future] = {}

    def start(self):
        if self._executor is None:
            self._executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=self.max_workers
            )

    def submit(self, name: str, func: Callable, *args, **kwargs) -> None:
        if self._executor is None:
            self.start()
        future = self._executor.submit(func, *args, **kwargs)
        self._futures[name] = future

    def get_result(self, name: str, timeout: Optional[float] = None) -> Any:
        future = self._futures.get(name)
        if future is None:
            return None
        try:
            return future.result(timeout=timeout)
        except Exception:
            return None

    def get_all_results(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        results = {}
        for name, future in self._futures.items():
            try:
                results[name] = future.result(timeout=timeout)
            except Exception as e:
                results[name] = {"error": str(e)}
        return results

    def shutdown(self, wait: bool = True):
        if self._executor:
            self._executor.shutdown(wait=wait)
            self._executor = None
        self._futures.clear()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()


class ProgressTracker:
    """Tracks progress of multiple concurrent tasks."""

    def __init__(self, total: int = 0):
        self._total = total
        self._completed = 0
        self._lock = threading.Lock()
        self._tasks: Dict[str, str] = {}  # name -> status

    def add_task(self, name: str):
        with self._lock:
            self._tasks[name] = "pending"
            self._total = len(self._tasks)

    def start_task(self, name: str):
        with self._lock:
            self._tasks[name] = "running"

    def complete_task(self, name: str):
        with self._lock:
            self._tasks[name] = "completed"
            self._completed += 1

    def fail_task(self, name: str, error: str = ""):
        with self._lock:
            self._tasks[name] = f"failed: {error}"
            self._completed += 1

    @property
    def progress(self) -> float:
        if self._total == 0:
            return 0.0
        with self._lock:
            return self._completed / self._total * 100

    @property
    def summary(self) -> str:
        with self._lock:
            done = self._completed
            total = self._total
        return f"[{done}/{total}] ({self.progress:.0f}%)"

    def __repr__(self) -> str:
        return f"<ProgressTracker {self.summary}>"
