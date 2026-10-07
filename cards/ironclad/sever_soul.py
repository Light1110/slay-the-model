"""
Ironclad Uncommon Attack card - Sever Soul
"""
from engine.runtime_api import add_action

from typing import List
from actions.base import Action
from actions.card import ExhaustCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


class ExhaustAllNonAttackAction(Action):
    """Exhaust every non-Attack card currently in hand, from the end of the hand forward."""

    def execute(self) -> None:
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return
        hand = list(player.card_manager.get_pile("hand"))
        for card in hand:
            if card.card_type != CardType.ATTACK:
                add_action(ExhaustCardAction(card=card, source_pile="hand"), to_front=True)


@register("card")
class SeverSoul(Card):
    """Exhaust non-Attack cards and deal damage"""

    card_type = CardType.ATTACK
    rarity = RarityType.UNCOMMON

    base_cost = 2
    base_damage = 16

    upgrade_damage = 22

    def on_play(self, targets: List[Creature] = []):
        add_action(ExhaustAllNonAttackAction())
        super().on_play(targets)