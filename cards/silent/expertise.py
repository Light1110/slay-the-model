"""Silent uncommon skill card - Expertise."""

from typing import List

from actions.card import DrawCardsAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Expertise(Card):
    """Draw until your hand reaches the magic number."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON

    base_cost = 1
    base_magic = {"hand_size": 6}

    upgrade_magic = {"hand_size": 7}

    def on_play(self, targets: List[Creature] = []):
        from actions.base import LambdaAction
        from engine.runtime_api import add_actions

        target_size = self.get_magic_value("hand_size")

        def queue_draw() -> None:
            def count() -> int:
                from engine.game_state import game_state

                player = game_state.player
                if player is None:
                    return 0
                return max(0, target_size - len(player.card_manager.get_pile("hand")))

            add_actions([DrawCardsAction(count=count)])

        add_actions([LambdaAction(queue_draw)])
