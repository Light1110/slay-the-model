"""
Ironclad Rare Attack card - Feed
"""

from typing import List
from actions.base import Action
from actions.combat import AttackAction, GainMaxHPAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Feed(Card):
    """Deal damage, if Fatal raise Max HP"""

    card_type = CardType.ATTACK
    rarity = RarityType.RARE

    base_cost = 1
    base_damage = 10
    base_max_health_gain = 3

    upgrade_damage = 12
    upgrade_max_health_gain = 4

    # todo: 斩杀 + 最大生命值的逻辑，写在 card新建的 on_fatal 函数里。这个函数被 DealDamageAction 调用
