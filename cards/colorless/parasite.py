"""
Colorless Curse card - Parasite
"""

from typing import List
from actions.base import Action
from actions.combat import ModifyMaxHpAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Parasite(Card):
    """Unplayable, lose 3 Max HP if removed from deck"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    upgradeable = False

    def on_remove(self) -> List[Action]:
        """Lose 3 Max HP when exhausted/removed from deck"""
        from actions.combat import ModifyMaxHpAction

        max_hp_loss = 3
        return [ModifyMaxHpAction(amount=-max_hp_loss)]
