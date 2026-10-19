"""Monotonic elapsed time, started with gameplay rather than module import."""
import time
from collections.abc import Callable


class RunClock:
    def __init__(self, clock: Callable[[], float] | None = None):
        self._clock = clock if clock is not None else time.monotonic
        self._elapsed = 0.0
        self._started_at: float | None = None

    @property
    def elapsed(self) -> float:
        return self._elapsed + (max(0.0, self._clock() - self._started_at)
                                if self._started_at is not None else 0.0)

    @elapsed.setter
    def elapsed(self, seconds: float) -> None:
        self._elapsed = max(0.0, float(seconds))
        if self._started_at is not None:
            self._started_at = self._clock()

    def start(self) -> None:
        if self._started_at is None:
            self._started_at = self._clock()

    def stop(self) -> None:
        self._elapsed = self.elapsed
        self._started_at = None

    def reset(self) -> None:
        self._elapsed = 0.0
        self._started_at = None
