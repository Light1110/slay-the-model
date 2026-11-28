"""Defect Creative AI power."""

from actions.card import AddCardAction
from engine.runtime_api import add_actions
from powers.base import Power, StackType
from utils.random import get_random_card
from utils.registry import register
from utils.types import CardType


@register("power")
class CreativeAIPower(Power):
    name = "Creative AI"
    description = "At the start of your turn, add a random Power card into your hand."
    stack_type = StackType.INTENSITY
    is_buff = True

    def on_turn_start(self):
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return

        actions = []
        for _ in range(self.amount):
            card = get_random_card(
                namespaces=[player.namespace],
                card_types=[CardType.POWER],
                exclude_card_ids=["defect.SelfRepair"],
                pool_kind="combat",
            )
            if card is not None:
                actions.append(AddCardAction(card=card, dest_pile="hand"))
        add_actions(actions)
