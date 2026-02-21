"""
Duplication power for combat effects.
Your next cards are played twice.
"""
from typing import List
from actions.base import Action
from cards.base import Card
from powers.base import Power, StackType
from utils.registry import register
from utils.types import CardType

@register("power")
class DuplicationPower(Power):
    """Your next X cards are played twice."""
    
    name = "Duplication"
    description = "Your next cards are played twice."
    stack_type = StackType.INTENSITY
    is_buff = True  # Beneficial effect - plays cards twice
    
    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        """
        Args:
            amount: Number of cards to duplicate (default 1)
            duration: 0 for permanent, positive for temporary turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card: Card, player, entities) -> List[Action]:
        return card.on_play() * self.amount