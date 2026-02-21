"""
Sadistic Nature power for combat effects.
Deal damage when applying debuff to enemy.
"""
from typing import List
from actions.base import Action
from actions.combat import DealDamageAction
from powers.base import Power
from utils.registry import register


@register("power")
class SadisticNaturePower(Power):
    """Deal damage when applying debuff to enemy."""

    name = "Sadistic Nature"
    description = "Deal damage when applying debuff to enemy."
    stackable = False
    amount_equals_duration = False
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = 0, owner=None):
        """
        Args:
            amount: Damage amount (default 5, upgraded 7)
            duration: 0 for permanent (this combat)
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_power_added(self, power, source=None) -> List[Action]:
        """Deal damage when a debuff is applied to an enemy by the player."""
        from engine.game_state import game_state
        
        actions = []
        
        if self.owner != game_state.player:
            return actions
        
        if not hasattr(power, 'is_buff') or power.is_buff:
            return actions
        
        if not hasattr(power, 'owner') or not power.owner:
            return actions
        
        target = power.owner
        if target == self.owner:
            return actions
        
        from entities.creature import Creature
        if not isinstance(target, Creature):
            return actions
        
        if target == game_state.player:
            return actions
        
        actions.append(DealDamageAction(
            damage=self.amount,
            target=target,
            source=self.owner,
            damage_type="hp_loss"
        ))
        
        return actions