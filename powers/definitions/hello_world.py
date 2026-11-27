"""Defect Hello World power."""

from actions.card import AddCardAction
from engine.runtime_api import add_actions
from powers.base import Power, StackType
from utils.random import get_random_card
from utils.registry import register
from utils.types import RarityType


@register("power")
class HelloWorldPower(Power):
    name = "Hello World"
    description = "At the start of your turn, add {amount} random Common card(s) to your hand."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        if self.stack_type == StackType.PRESENCE:
            # Older pickles stored one active application with a zero amount.
            self.stack_type = StackType.INTENSITY
            self.amount = 1

    def on_turn_start(self):
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return
        actions = []
        for _ in range(self.amount):
            card = get_random_card(
                namespaces=[player.namespace],
                rarities=[RarityType.COMMON],
                pool_kind="current",
            )
            if card is not None:
                actions.append(AddCardAction(card=card, dest_pile="hand"))
        add_actions(actions)
