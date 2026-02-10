"""
Ironclad Rare Skill card - Double Tap
"""

from typing import List
from actions.base import Action
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class DoubleTap(Card):
    """This turn, your next 1/2 Attack is played twice"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1

    base_magic = {"double_card_num": 1}
    upgrade_magic = {"double_card_num": 2}
    
    # todo: ApplyPowerAction: DoubleTapPower
