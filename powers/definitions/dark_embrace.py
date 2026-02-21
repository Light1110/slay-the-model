"""
Dark Embrace power for Ironclad.
Whenever a card is exhausted, draw 1 card.
"""
from typing import List, Any
from powers.base import Power, StackType
from actions.base import Action
from actions.card import DrawCardsAction
from utils.registry import register


@register("power")
class DarkEmbracePower(Power):
    """Whenever a card is exhausted, draw 1 card."""

    name = "Dark Embrace"
    description = "Whenever a card is exhausted, draw 1 card."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: card to draw
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_exhaust(self) -> List[Action]:
        """Draw 1 card when any card is exhausted."""
        return [DrawCardsAction(count=self.amount)]
