"""
Weak power for combat effects.
Reduces damage dealt by 25%.
"""
from typing import Any, List
from powers.base import Power, StackType
from utils.damage_phase import DamagePhase
from utils.registry import register


@register("power")
class WeakPower(Power):
    """Reduce damage dealt by 25%."""
    
    name = "Weak"
    description = "Reduces damage dealt by 25%."
    stack_type = StackType.DURATION
    decays_at_round_end = True
    is_buff = False  # Debuff - reduces damage dealt
    modify_phase = DamagePhase.MULTIPLICATIVE
    damage_priority = 99
    
    def __init__(self, amount: int = 0, duration: int = 2, owner=None):
        """
        Args:
            amount: Weak stacks (default 2)
            duration: Duration in turns (default 2)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
    
    def modify_damage_dealt(self, base_damage: int) -> float:
        """Reduce damage dealt by 25%."""
        return base_damage * 0.75