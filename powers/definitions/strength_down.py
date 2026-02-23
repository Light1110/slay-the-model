"""
Strength Down power for temporary strength effects.
Loses strength at end of turn.
"""
from typing import List
from actions.base import Action
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class StrengthDownPower(Power):
    """Lose strength at end of turn."""

    name = "Strength Down"
    description = "Lose {amount} Strength at the end of your turn."
    stack_type = StackType.INTENSITY
    is_buff = False

    def __init__(self, amount: int = 2, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        """Lose strength and remove this power."""
        from actions.combat import ApplyPowerAction
        from engine.game_state import game_state
        from powers.definitions.strength import StrengthPower
        
        actions = []
        
        if self.owner:
            actions.append(ApplyPowerAction(
                StrengthPower(amount=-self.amount, owner=self.owner),
                self.owner
            ))
        
        return actions
