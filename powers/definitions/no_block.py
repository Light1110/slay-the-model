"""
No Block power for combat effects.
Prevents gaining block for duration.
"""
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
        
        # todo: Implement in GainBlockAction
