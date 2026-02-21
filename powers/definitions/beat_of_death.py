"""
Beat of Death power for Corrupt Heart boss.
Deals damage to player whenever they play a card.
"""
from typing import List

from actions.base import Action
from actions.combat import AttackAction
from powers.base import Power
from utils.registry import register


@register("power")
class BeatOfDeathPower(Power):
    """Whenever the player plays a card, deal damage to them."""

    name = "Beat of Death"
    description = "Whenever you play a card, take damage."
    stackable = True
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = 0, owner=None):
        """
        Args:
            amount: Damage dealt per card played
            duration: 0 for permanent (doesn't decay)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_card_play(self, card, player, entities) -> List[Action]:
        """Deal damage to player when they play a card."""
        if player is None or self.owner is None:
            return []
        return [
            AttackAction(
                damage=self.amount,
                target=player,
                source=self.owner,
                damage_type="beat_of_death",
            )
        ]