"""
Ironclad Rare Skill card - Exhume
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction # todo: 实现 MoveCardAction && ChooseMoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Exhume(Card):
    """Choose a card from your Exhaust pile and add it to your hand"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 1
    base_exhaust = True
    upgrade_cost = 0

    def on_play(self, target: Creature | None = None) -> List[Action]:
        actions = super().on_play(target)

        # Choose a card from exhaust pile
        actions.append(ChooseMoveCardAction(src="exhaust_pile", dst="hand", amount=1))

        return actions
