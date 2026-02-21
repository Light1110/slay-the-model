"""
No Block power for combat effects.
Prevents gaining block for duration.
"""
from __future__ import annotations
from typing import List
from powers.base import Power
from utils.registry import register


@register("power")
class NoBlockPower(Power):
    """Cannot gain block for duration."""

    name = "No Block"
    description = "Cannot gain block."
    stackable = False
    amount_equals_duration = False
    is_buff = False

    def __init__(self, amount: int = 1, duration: int = 2, owner=None):
        """
        Args:
            amount: Not used (power is binary)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def on_gain_block(self, amount: int, player=None, source=None, card=None) -> List['Action']:
        """Prevent all block gain."""
        if player == self.owner:
            return []
        return super().on_gain_block(amount, player, source, card)
