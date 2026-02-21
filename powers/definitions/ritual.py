"""
Ritual power for combat effects.
Gain Strength at end of turn.
"""
from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from powers.definitions.strength import StrengthPower
from utils.registry import register

@register("power")
class RitualPower(Power):
    """Gain Strength at end of turn."""
    
    name = "Ritual"
    description = "Gain Strength at end of turn."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect - increases strength
    
    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Strength to gain each turn (default 1)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_turn_end(self) -> List[Action]:
        return super().on_turn_end() + [ApplyPowerAction(StrengthPower(), self.owner, self.amount)]
