from typing import Optional
from actions.base import Action
from cards.base import COST_UNPLAYABLE, Card
from actions.combat import DealDamageAction
from utils.dynamic_values import get_magic_value
from utils.result_types import List
from utils.types import CardType


class Burn(Card):
    """Burn card - deals damage to owner at end of turn"""
    base_cost = COST_UNPLAYABLE
    card_type = CardType.STATUS
    
    base_magic = {"burn_damage": 2}
    upgrade_magic = {"burn_damage": 4}

    def on_turn_end(self) -> List[Action]:
        """Deal damage to player at end of turn"""
        from engine.game_state import game_state
        actions = super().on_player_turn_end()
        actions.append(DealDamageAction(
            damage=get_magic_value(self, "burn_damage"),
            target=game_state.player,
            direct=True
        ))
        return actions
