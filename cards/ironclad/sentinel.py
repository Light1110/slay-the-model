"""
Ironclad Uncommon Skill card - Sentinel
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction, ApplyPowerAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Sentinel(Card):
    """Gain 5/8 block. On exhausted, gain 2/3 energy"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_block = 5

    upgrade_block = 8
    
    base_magic = {"energy_on_exhaust": 2}
    upgrade_magic = {"energy_on_exhaust": 3}

    # todo: 获得能量，写在 on_exhaust 里面
