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

    # todo hook: 当这个能力的持有者 *被施加了能力*