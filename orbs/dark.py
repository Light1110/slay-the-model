from typing import List

from actions.base import Action, LambdaAction
from actions.combat import DealDamageAction
from orbs.base import Orb
from utils.combat import resolve_target
from utils.dynamic_values import resolve_orb_value
from utils.types import TargetType


class DarkOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_LOWEST_HP
    base_charge = 6

    def __init__(self):
        self.charge = self.base_charge

    def on_passive(self) -> List[Action]:
        return [
            LambdaAction(
                func=lambda: setattr(self, "charge", self.charge + resolve_orb_value(self.base_charge))
            )
        ]

    def on_evoke(self) -> List[Action]:
        target_list = resolve_target(self.target_type)
        target = target_list[0] if target_list else None
        if target is None:
            return []
        damage = self.charge
        if target.get_power("Lock-On") is not None:
            damage = int(damage * 1.5)
        return [
            DealDamageAction(
                damage=damage,
                target=target,
                damage_type="magic",
            )
        ]
