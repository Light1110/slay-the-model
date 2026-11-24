"""
Colorless Rare Skill card - Violence
"""
from engine.random_streams import StreamRandom, get_rng
from engine.runtime_api import add_action

from typing import List, cast
from actions.base import Action
from actions.card import MoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.dynamic_values import get_magic_value
from utils.registry import register
from utils.types import CardType, RarityType


@register("action")
class ViolenceSelectionAction(Action):
    """Move selected attacks from the current draw pile into hand."""

    def __init__(self, amount: int):
        self.amount = amount

    def execute(self) -> None:
        from engine.game_state import game_state

        player = game_state.player
        if player is None:
            return

        candidates = []
        card_rng = cast(StreamRandom, get_rng("card_random"))
        for card in player.card_manager.get_pile("draw_pile"):
            if card.card_type != CardType.ATTACK:
                continue
            if candidates:
                candidates.insert(card_rng.random_int(len(candidates) - 1), card)
            else:
                candidates.append(card)

        shuffle_rng = get_rng("shuffle")
        for _ in range(min(self.amount, len(candidates))):
            shuffle_rng.shuffle(candidates)
            card = candidates.pop(0)
            MoveCardAction(card, src_pile="draw_pile", dst_pile="hand").execute()


@register("card")
class Violence(Card):
    """Put random Attacks from draw pile into hand, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_magic = {"cards": 3}
    base_exhaust = True
    
    upgrade_magic = {"cards": 4}

    def on_play(self, targets: List[Creature] = []):
        super().on_play(targets)
        add_action(ViolenceSelectionAction(get_magic_value(self, "cards")))
