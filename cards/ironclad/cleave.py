"""
Ironclad Common Attack card - Cleave
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Cleave(Card):
    """Deal damage to ALL enemies"""

    card_type = CardType.ATTACK
    rarity = RarityType.COMMON
    target_type = TargetType.ENEMY_ALL

    base_cost = 1
    base_damage = 8

    upgrade_damage = 11
