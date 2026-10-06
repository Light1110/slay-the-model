"""
Entangled power for combat effects.
Prevents playing Attack cards for duration.
"""
from typing import Any, List
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class EntangledPower(Power):
    """Cannot play Attack cards."""
    
    name = "Entangled"
    description = "Cannot play Attack cards."
    stack_type = StackType.PRESENCE
    is_buff = False  # Debuff - prevents playing Attack cards
    
    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        """
        Args:
            amount: Not used (power is binary)
            duration: Duration in turns (default 1)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def allows_card_play(self, card):
        """Attacks cannot be played while this debuff is active."""
        from utils.types import CardType

        if getattr(card, "card_type", None) == CardType.ATTACK:
            return False, "Entangled restriction"
        return True, None
