"""Fading power for combat effects.
Owner dies when countdown reaches zero.
"""

from typing import List

from actions.base import Action
from powers.base import Power
from utils.registry import register


@register("power")
class FadingPower(Power):
    """Die when fading countdown expires."""

    name = "Fading"
    description = "Dies in {amount} turns."
    stackable = False
    amount_equals_duration = True
    is_buff = True

    def __init__(self, duration: int = 5, owner=None):
        super().__init__(amount=duration, duration=duration, owner=owner)

    def on_turn_end(self) -> List[Action]:
        actions = super().on_turn_end()
        if self.owner and self.duration == 0 and not self.owner.is_dead():
            self.owner.hp = 0
            death_actions = self.owner.on_death()
            if death_actions:
                actions.extend(death_actions)
        return actions
