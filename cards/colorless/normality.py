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
    
    def on_draw(self):
        from engine.game_state import game_state
        combat = game_state.current_combat
        assert combat is not None
        if combat.combat_state.turn_cards_played >= 3:
            combat.combat_state.turn_enable_card_play = False
        return