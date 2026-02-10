"""
Colorless Status card - Void
"""

from typing import List
from actions.base import Action
from actions.combat import GainEnergyAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Void(Card):
    """Unplayable, lose 1 energy when drawn, Ethereal"""

    card_type = CardType.STATUS
    rarity = RarityType.COMMON

    base_cost = COST_UNPLAYABLE
    base_ethereal = True
    upgradeable = False

    def on_draw(self) -> List[Action]:
        """Lose 1 energy when drawn"""
        from actions.combat import GainEnergyAction

        return [GainEnergyAction(energy=-1)]
