"""
Colorless Curse card - Shame
"""

from typing import List
from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card, COST_UNPLAYABLE
from powers.definitions.frail import FrailPower
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Shame(Card):
    """Unplayable, gain 1 Frail at end of turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    upgradeable = False

    def on_player_turn_end(self) -> List[Action]:
        """Gain 1 Frail at end of turn"""
        from engine.game_state import game_state

        actions = super().on_player_turn_end()

        frail_amount = 1
        actions.append(ApplyPowerAction(
            FrailPower(amount=frail_amount, duration=frail_amount, owner=game_state.player),
            game_state.player
        ))

        return actions
