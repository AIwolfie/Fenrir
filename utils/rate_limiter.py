"""Request throttling helpers for asynchronous crawlers in DeepRecon.

Author: AIwolfie
Repository: https://github.com/AIwolfie/DeepRecon
"""

from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """A minimal async rate limiter with a fixed delay between requests."""

    def __init__(self, delay: float) -> None:
        self.delay = max(0.0, delay)
        self._lock = asyncio.Lock()
        self._next_allowed_at = 0.0

    async def wait(self) -> None:
        """Sleep until the next request is allowed."""

        async with self._lock:
            now = time.monotonic()
            sleep_for = max(0.0, self._next_allowed_at - now)
            self._next_allowed_at = max(self._next_allowed_at, now) + self.delay
        if sleep_for > 0:
            await asyncio.sleep(sleep_for)
