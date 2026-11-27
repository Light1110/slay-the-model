"""Defect uncommon skill card - White Noise."""

from typing import List

from actions.card import AddCardAction
from cards.base import Card
from entities.creature import Creature
from utils.random import get_random_card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class WhiteNoise(Card):
    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    upgrade_cost = 0
    base_exhaust = True

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        from engine.game_state import game_state
        from engine.runtime_api import add_action

        card = get_random_card(
            namespaces=[game_state.player.namespace],
            card_types=[CardType.POWER],
            exclude_card_ids=["defect.SelfRepair"],
            pool_kind="combat",
        )
        if card is not None:
            card.cost_until_end_of_turn = 0
            add_action(AddCardAction(card=card, dest_pile="hand"))
