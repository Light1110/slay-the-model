"""
Frail power for combat effects.
Reduce block gained by 25%.
"""
from typing import List
from powers.base import Power, StackType
from utils.damage_phase import DamagePhase
from utils.registry import register


@register("power")
class FrailPower(Power):
    """Reduce block gained by 25%."""

    name = "Frail"
    description = "Reduce block gained by 25%."
    stack_type = StackType.DURATION
    decays_at_round_end = True
    amount_equals_duration = True
    is_buff = False
    modify_phase = DamagePhase.MULTIPLICATIVE

    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        """
        Args:
            amount: Frail stacks (default 1)
            duration: Duration in turns (default 1)
        """
        if duration < 0 and amount > 0:
            duration = amount
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def modify_block_gained(self, base_block: int) -> float:
        """Reduce block gained from cards by 25%."""
        return base_block * 0.75
