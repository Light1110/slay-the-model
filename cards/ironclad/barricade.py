"""
Ironclad Rare Power card - Barricade
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Barricade(Card):
    """Block does not expire at the start of your turn"""

    card_type = CardType.POWER
    rarity = RarityType.RARE

    base_cost = 3
    
    # todo: add BarricadePower to player
