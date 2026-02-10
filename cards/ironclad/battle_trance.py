"""
Ironclad Uncommon Skill card - Battle Trance
"""

from typing import List
from actions.base import Action
from actions.combat import GainBlockAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class BattleTrance(Card):
    """Draw 3/4 cards. Cannot draw cards this turn."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    # todo
    # DrawCardAction + ApplyPowerAction
