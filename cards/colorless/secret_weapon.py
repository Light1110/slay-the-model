"""
Colorless Rare Skill card - Secret Weapon
"""

from typing import List
from actions.base import Action
from actions.card import ChooseMoveCardAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class SecretWeapon(Card):
    """Put Attack from draw pile into hand, Exhaust"""

    card_type = CardType.SKILL
    rarity = RarityType.RARE

    base_cost = 0
    base_exhaust = True
    upgrade_exhaust = False

    # Note: Upgraded version removes Exhaust flag

    def on_play(self, target: Creature | None = None) -> List[Action]:
        from engine.game_state import game_state

        actions = super().on_play(target)

        # Move an Attack from draw pile to hand
        if game_state.player and hasattr(game_state.player, "card_manager"):
            actions.append(ChooseMoveCardAction(
                src="draw_pile",
                dst="hand",
                amount=1,
                filter_card_type=CardType.ATTACK
            ))

        return actions
