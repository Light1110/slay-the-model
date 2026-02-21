"""
Feel No Pain power for Ironclad.
Whenever you exhaust one card, gain block.
"""
from typing import List
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import GainBlockAction
from utils.registry import register


@register("power")
class FeelNoPainPower(Power):
    """Whenever you exhaust one card, gain 3/4 block."""

    name = "Feel No Pain"
    description = "Whenever you exhaust one card, gain block."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 3, duration: int = -1, owner=None):
        """
        Args:
            amount: Block to gain per exhaust (default 3)
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_exhaust(self) -> List[Action]:
        """Gain block when a card is exhausted."""
        from engine.game_state import game_state
        actions = []

        if game_state.player:
            actions.append(GainBlockAction(block=self.amount, target=game_state.player))

        return actions
