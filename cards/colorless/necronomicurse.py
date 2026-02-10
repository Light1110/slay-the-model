"""
Colorless Special Curse card - Necronomicurse
"""

from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Necronomicurse(Card):
    """Unplayable, Irremovable"""

    card_type = CardType.CURSE
    rarity = RarityType.SPECIAL

    base_cost = COST_UNPLAYABLE
    removable = False
    upgradeable = False
