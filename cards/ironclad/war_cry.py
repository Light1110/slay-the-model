"""
Ironclad Common Skill card - War Cry
"""

from typing import List
from actions.base import Action
from actions.card import DrawCardsAction, ChooseMoveCardAction # todo: ChooseMoveCardAction 
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class WarCry(Card):
    """Draw cards and put a card on top of draw pile"""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 0
    base_draw = 1

    upgrade_draw = 2

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Draw cards
        actions.append(DrawCardsAction(count=self.draw))

        actions.append(ChooseMoveCardAction(src="hand", dst="draw_pile", amount=1))

        return actions
