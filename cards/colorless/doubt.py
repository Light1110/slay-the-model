"""
Colorless Curse card - Doubt
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Doubt(Card):
    """Unplayable, gain 1 Weak at end of turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    upgradeable = False

    def on_player_turn_end(self) -> List[Action]:
        """Gain 1 Weak at end of turn"""
        from engine.game_state import game_state

        actions = super().on_player_turn_end()

        weak_amount = 1
        actions.append(ApplyPowerAction(
            power="Weak",
            target=game_state.player,
            amount=weak_amount
        ))

        return actions
