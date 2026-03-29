"""
Flame Barrier power for Ironclad.
Gain block, deal damage to enemies that attack.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, Any
from actions.base import Action
from powers.base import Power, StackType
from actions.combat import DealDamageAction
from utils.registry import register


@register("power")
class FlameBarrierPower(Power):
    """Gain block. Deal damage to enemies that attack you."""

    name = "Flame Barrier"
    description = "Deal damage to enemies that attack you."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 5, duration: int = 1, owner=None):
        """
        Args:
            amount: Not used
            duration: Duration in turns
        """
        super().__init__(amount=amount, duration=duration, owner=owner)

    def on_damage_taken(self, damage: int, source: Any = None, card: Any = None,
                       player: Any = None, damage_type: str = "direct"):
        """Deal damage to attacker when this creature is attacked."""

        if damage_type == "attack":
            # Deal damage back to attacker
            from engine.game_state import game_state
            add_action(DealDamageAction(
                damage=self.amount,
                target=source,
                damage_type="power",
                source=self.owner if self.owner else None,
                card=None
            ))
            return

        return
