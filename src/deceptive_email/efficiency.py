"""Efficiency measurement: timing, memory monitoring, and resource recording."""
from __future__ import annotations

import threading
import time

import psutil


class MemoryMonitor:
    """Samples the current process RSS in a background thread and records the peak."""

    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.process = psutil.Process()
        self.peak_gb = 0.0
        self.baseline_gb = 0.0
        self._stop = threading.Event()
        self._thread = None

    def __enter__(self):
        self.baseline_gb = self.process.memory_info().rss / (1024 ** 3)
        self.peak_gb = self.baseline_gb
        self._thread = threading.Thread(target=self._sample, daemon=True)
        self._thread.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2)

    def _sample(self):
        while not self._stop.is_set():
            try:
                gb = self.process.memory_info().rss / (1024 ** 3)
                if gb > self.peak_gb:
                    self.peak_gb = gb
            except psutil.Error:
                pass
            self._stop.wait(self.interval)

    def peak_gb_above_baseline(self) -> float:
        return max(0.0, self.peak_gb - self.baseline_gb)


def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    return result, time.perf_counter() - t0
