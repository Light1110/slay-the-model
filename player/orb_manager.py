"""Orb management for the player."""

from typing import List, Optional
from orbs.base import Orb

class OrbManager:
    """Manages orbs for the player."""

    def __init__(self, max_orb_slots: int = 1) -> None:
        self._orbs: List[Orb] = []
        self._max_orb_slots = max_orb_slots

    @property
    def orbs(self) -> List[Orb]:
        return self._orbs

    @property
    def max_orb_slots(self) -> int:
        return self._max_orb_slots

    @max_orb_slots.setter
    def max_orb_slots(self, value: int) -> None:
        value = max(0, int(value))
        if value < self._max_orb_slots:
            self._orbs = self._orbs[:value]
        self._max_orb_slots = value

    def add_orb(self, orb: Orb) -> None:
        """Add an orb. If max slots exceeded, evoke rightmost orb first."""
        if self._max_orb_slots <= 0:
            return
        if len(self._orbs) >= self._max_orb_slots:
            self.evoke_orb()
        self._orbs.append(orb)

    def evoke_orb(self, index: int = 0, times : int = 1) -> Optional[Orb]:
        """Evoke an orb (remove and return it). Defaults to rightmost orb."""
        if not self._orbs:
            return None
        if index < 0 or index >= len(self._orbs):
            return None
        for _ in range(times):
            self._orbs[index].evoke()
        return self._orbs.pop(index)

    def remove_orb(self, index: int = 0) -> Optional[Orb]:
        """Remove an orb at specific index without evoking. Defaults to rightmost orb."""
        if not self._orbs or index < 0 or index >= len(self._orbs):
            return None
        return self._orbs.pop(index)

    def clear_all(self) -> None:
        """Remove all orbs without evoking."""
        self._orbs.clear()
        
    def evoke_all(self) -> Optional[List[Orb]]:
        """Evoke all orbs."""
        if not self._orbs:
            return None
        evoked_orbs = []
        while self._orbs:
            orb = self._orbs.pop(0)
            orb.evoke()
            evoked_orbs.append(orb)
        return evoked_orbs

    def get_orb_count(self) -> int:
        """Get current number of orbs."""
        return len(self._orbs)

    def trigger_passives(self, timing: str) -> None:
        """Trigger orb passives based on timing."""
        for orb in list(self._orbs):
            if getattr(orb, "passive_timing", None) == timing:
                orb.passive()
