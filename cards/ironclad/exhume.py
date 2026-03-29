"""
Ironclad Rare Skill card - Exhume
"""
from engine.runtime_api import add_action, add_actions

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction
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

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state

        add_action(
            ChooseMoveCardAction(src="exhaust_pile", dst="hand", amount=1)
        )
        return
