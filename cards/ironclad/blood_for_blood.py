"""
Ironclad Uncommon Attack card - Blood for Blood
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BloodForBlood(Card):
    """Deal damage, costs less for each HP lost this combat"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 4
    base_damage = 18

    upgrade_damage = 22

    # todo: cost reduction 通过 on_damage_taken 更改 
