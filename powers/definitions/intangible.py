"""
Intangible power for combat effects.
Reduce all damage taken to 1.
"""
from typing import List
from powers.base import Power
from utils.registry import register


@register("power")
class IntangiblePower(Power):
    """Reduce all damage taken to 1."""

    name = "Intangible"
    description = "Reduce all damage taken to 1."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 1, owner=None):
        """
        Args:
            amount: Not used (duration controls effect)
            duration: Duration in turns (default 1)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
