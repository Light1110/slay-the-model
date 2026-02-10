"""
Ironclad Uncommon Attack card - Whirlwind
"""

from cards.base import Card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Whirlwind(Card):
    """Deal damage to ALL enemies X times"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = "X"  # X cost card
    base_damage = 5
    upgrade_damage = 8

    @property
    def attack_times(self) -> int:
        return self.cost # feature: X药，+2