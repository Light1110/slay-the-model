"""Strength Up power for temporary strength restoration.
Gains Strength at end of turn, then expires.
"""

from typing import List

from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power, StackType
from utils.registry import register


@register("power")
class StrengthUpPower(Power):
    """Gain Strength at end of turn and then remove itself."""

    name = "Strength Up"
    description = "At the end of turn, gain {amount} Strength."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 0, duration: int = 1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        actions: List[Action] = []
        if self.owner and self.amount:
            actions.append(
                ApplyPowerAction(
                    power="Strength",
                    target=self.owner,
                    amount=self.amount,
                )
            )
        self.duration = 0
        return actions
