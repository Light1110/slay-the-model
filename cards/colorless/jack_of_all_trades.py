"""
Colorless Uncommon Skill card - Jack of All Trades
"""
from engine.runtime_api import add_actions

from typing import List
from actions.card import AddCardAction
from cards.base import Card
from entities.creature import Creature
from utils.random import get_random_card
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class JackOfAllTrades(Card):
    """Add random colorless card(s), Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 0
    base_magic = {"cards": 1}
    base_exhaust = True

    upgrade_magic = {"cards": 2}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        actions = []
        for _ in range(self.get_magic_value("cards")):
            card = get_random_card(namespaces=["colorless"], pool_kind="combat")
            if card is not None:
                actions.append(AddCardAction(card=card, dest_pile="hand"))
        add_actions(actions)
