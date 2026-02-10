"""
Ironclad Uncommon Power card - Evolve
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Evolve(Card):
    """Whenever you draw a status card, draw 1/2"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    
    # todo: ApplyPowerAction: EvolvePower
