"""Corpse Explosion death trigger power."""

from actions.combat import DealDamageAction
from engine.messages import EnemyHpDepletedMessage
from engine.subscriptions import MessagePriority, subscribe
from powers.base import Power, StackType
from utils.registry import register
from utils.types import DamageType


@register("power")
class CorpseExplosionPower(Power):
    name = 'Corpse Explosion'
    description = 'When this enemy dies, deal damage to all enemies equal to its max HP.'
    stack_type = StackType.INTENSITY
    is_buff = False

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)

    @subscribe(EnemyHpDepletedMessage, priority=MessagePriority.REACTION)
    def on_hp_depleted(self):
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        if self.owner is None or self.owner.hp > 0 or game_state.current_combat is None:
            return
        # Capture the amount before the owner's half-dead cleanup removes us.
        damage = self.owner.max_hp * self.amount
        actions = [
            DealDamageAction(
                damage=damage,
                target=enemy,
                damage_type=DamageType.THORNS,
            )
            for enemy in game_state.current_combat.enemies
            if enemy is not self.owner and enemy.hp > 0
        ]
        add_actions(actions)
