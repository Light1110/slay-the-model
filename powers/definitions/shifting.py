"""Shifting power for Transient.
Upon losing HP, apply temporary Strength loss and end-of-turn restoration.
"""

from typing import Any, List

from actions.base import Action
from actions.combat import ApplyPowerAction
from powers.base import Power
from powers.definitions.strength_up import StrengthUpPower  # noqa: F401
from utils.registry import register


@register("power")
class ShiftingPower(Power):
    """On damage taken, lose that much Strength until end of turn."""

    name = "Shifting"
    description = "Upon losing HP, loses that much Strength until the end of turn."
    stackable = False
    is_buff = True

    def __init__(self, owner=None):
        super().__init__(amount=0, duration=-1, owner=owner)

    def on_damage_taken(
        self,
        damage: int,
        source: Any = None,
        card: Any = None,
        player: Any = None,
        damage_type: str = "direct",
    ) -> List[Action]:
        if not self.owner or damage <= 0:
            return []

        actions: List[Action] = [
            ApplyPowerAction(
                power="Strength",
                target=self.owner,
                amount=-damage,
            )
        ]

        strength_up = self.owner.get_power("strength up")
        if strength_up:
            strength_up.amount += damage
            strength_up.duration = 1
        else:
            actions.append(
                ApplyPowerAction(
                    power="StrengthUp",
                    target=self.owner,
                    amount=damage,
                    duration=1,
                )
            )

        return actions
