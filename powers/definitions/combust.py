"""
Combust power for Ironclad.
At end of turn, deal damage to all enemies.
"""
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import DealDamageAction, LoseHPAction
from utils.registry import register


@register("power")
class CombustPower(Power):
    """At end of turn, lose 1 heal and deal damage to all enemies."""

    name = "Combust"
    description = "At end of turn, deal damage to all enemies."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = -1, owner=None):
        """
        Args:
            amount: Damage to deal each turn
            duration: 0 for permanent
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        """Deal damage to all enemies at end of turn."""
        from engine.game_state import game_state
        player = game_state.player
        actions = []
        
        actions.append(LoseHPAction(damage=1, target=player))

        if game_state.current_combat:
            enemies = game_state.current_combat.enemies
            for enemy in enemies:
                if enemy.hp > 0:
                    actions.append(DealDamageAction(
                        damage=self.amount,
                        target=enemy,
                        damage_type="direct",
                        source=self,
                        card=None
                    ))

        # Call parent method to handle duration tick
        return super().on_turn_end() + actions
