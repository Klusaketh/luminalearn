"""
In-process sliding-window rate limiting for AI endpoints.

AI turns spend model quota, so the tutor and voice endpoints cap turns per learner (or per
client address for guests). Limits are per worker process, which is sufficient abuse
protection for a single-node deployment.
"""
import time
from collections import deque


class SlidingWindowRateLimiter:
    """Counts events per key inside a rolling window."""

    _PRUNE_THRESHOLD = 10_000

    def __init__(self, window_s: int) -> None:
        self.window_s = window_s
        self._events: dict[str, deque[float]] = {}

    def hit(self, key: str, limit: int) -> float | None:
        """Records one event. Returns None when allowed, else seconds until a slot frees up."""
        now = time.monotonic()
        events = self._events.setdefault(key, deque())
        while events and now - events[0] >= self.window_s:
            events.popleft()
        if len(events) >= limit:
            return max(1.0, self.window_s - (now - events[0])) if events else float(self.window_s)
        events.append(now)
        if len(self._events) > self._PRUNE_THRESHOLD:
            self._prune(now)
        return None

    def _prune(self, now: float) -> None:
        stale = [key for key, events in self._events.items() if not events or now - events[-1] >= self.window_s]
        for key in stale:
            del self._events[key]
