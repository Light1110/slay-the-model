"""
Ironclad Rare Attack card - Reaper
"""

from typing import List
from actions.base import Action
from actions.combat import AttackAction, HealAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


@register("card")
class Reaper(Card):
    """Deal damage to ALL enemies, heal for unblocked damage"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE
    target_type = TargetType.ENEMY_ALL

    base_cost = 2
    base_damage = 4

    upgrade_damage = 5

    # todo: 吸血逻辑写在 on_damage_dealt 里面