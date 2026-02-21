"""
Battle Trance Draw power for Ironclad.
Cannot draw cards this turn.
"""
from typing import List, Any
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class BattleTranceDrawPower(Power):
    """Cannot draw cards this turn."""

    name = "Battle Trance (Cannot Draw)"
    description = "Cannot draw cards this turn."
    stack_type = StackType.DURATION
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        """
        Args:
            amount: Not used
            duration: Duration in turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
