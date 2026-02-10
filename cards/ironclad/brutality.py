"""
Ironclad Rare Power card - Brutality
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Brutality(Card):
    """At the start of your turn, lose 1 HP and draw 1 card"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 0
    upgrade_innate = True
    
    # todo: ApplyPowerAction: BrutalityPower
