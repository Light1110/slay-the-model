"""
Ironclad Uncommon Power card - Combust
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Combust(Card):
    """At end of turn, deal 5/7 damage to all enemy"""

    card_type = CardType.POWER
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"combust_damage": 5}
    upgrade_magic = {"combust_damage": 7}
    
    # todo: ApplyPowerAction: CombustPower
