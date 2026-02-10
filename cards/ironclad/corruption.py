"""
Ironclad Rare Power card - Corruption
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Corruption(Card):
    """Skills cost 0"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    upgrade_cost = 2
    
    # todo: ApplyPowerAction: CorruptionPower
