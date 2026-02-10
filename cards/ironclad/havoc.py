"""
Ironclad Common Skill card - Havoc
"""

from typing import List
from actions.base import Action
from actions.card import ExhaustCardAction
from actions.combat import PlayCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Havoc(Card):
    """Play top card of draw pile and exhaust it"""

    card_type = CardType.SKILL
    rarity = RarityType.COMMON

    base_cost = 1

    upgrade_cost = 0

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Play top card of draw pile
        draw_pile = game_state.player.card_manager.get_pile('draw_pile')
        card_to_play = draw_pile[0] # ? 堆顶是0还是-1
        actions.append(PlayCardAction(card=card_to_play))
        actions.append(ExhaustCardAction(card=card_to_play))

        return actions
