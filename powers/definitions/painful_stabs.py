"""
Painful Stabs power for Corrupt Heart boss.
Adds a Wound to discard pile whenever player plays an Attack.
"""
from typing import List

from actions.base import Action
from actions.card import AddCardAction
from cards.colorless.wound import Wound
from powers.base import Power
from utils.registry import register
from utils.types import CardType


@register("power")
class PainfulStabsPower(Power):
    """Whenever the player plays an Attack, add a Wound."""

    name = "Painful Stabs"
    description = "Whenever you play an Attack, shuffle a Wound into discard."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        """
        Args:
            amount: Not used for this power (non-stackable)
            duration: 0 for permanent (doesn't decay)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, player, entities) -> List[Action]:
        """Add a Wound to discard pile when player plays an Attack."""
        if card is None or getattr(card, "card_type", None) != CardType.ATTACK:
            return []
        return [AddCardAction(card=Wound(), dest_pile="discard_pile")]