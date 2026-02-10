"""
Colorless Curse card - Decay
"""

from typing import List
from actions.base import Action
from actions.combat import DealDamageAction
from cards.base import Card, COST_UNPLAYABLE
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Decay(Card):
    """Unplayable, deal 2 damage at end of turn"""

    card_type = CardType.CURSE
    rarity = RarityType.CURSE

    base_cost = COST_UNPLAYABLE
    base_magic = {"turn_end_damage": 2}
    upgradeable = False

    def on_player_turn_end(self) -> List[Action]:
        """Deal damage at end of turn"""
        from engine.game_state import game_state

        actions = super().on_player_turn_end()

        damage_amount = self.get_magic_value("turn_end_damage")
        actions.append(DealDamageAction(
            damage=damage_amount,
            target=game_state.player,
            damage_type='card'
        ))

        return actions
