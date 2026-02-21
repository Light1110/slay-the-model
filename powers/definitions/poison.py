"""
Poison power for combat effects.
Lose HP at start of turn, then reduce by 1.
"""
from typing import List
from actions.base import Action
from actions.combat import LoseHPAction
from powers.base import Power, StackType
from utils.registry import register

@register("power")
class PoisonPower(Power):
    """Lose HP at start of turn, then reduce by 1."""
    
    name = "Poison"
    description = "Lose HP at start of turn, then reduce by 1."
    stack_type = StackType.LINKED
    is_buff = False  # Debuff - loses HP over time
    
    def __init__(self, amount: int = 3, duration: int = 3, owner=None):
        """
        Args:
            amount: Poison damage per tick (default 3)
            duration: Duration in turns (default 3)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)
        
    def on_turn_start(self) -> List[Action]:
        actions = [LoseHPAction(amount=self.amount)]
        # Reduce poison by 1 after dealing damage
        self.amount = max(0, self.amount - 1)
        return actions
