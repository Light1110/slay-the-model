"""
Colorless Curse card - Normality
"""

from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Normality(Card):
    """Unplayable, can't play more than 3 cards this turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    upgradeable = False

    def allows_card_play(self, card):
        """While this curse is in hand, at most 3 cards can be played this turn."""
        from engine.game_state import game_state

        combat = game_state.current_combat
        if combat is not None and combat.combat_state.turn_cards_played >= 3:
            return False, "Normality restriction"
        return True, None
