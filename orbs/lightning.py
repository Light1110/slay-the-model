from typing import List

from actions.base import Action
from actions.combat import DealDamageAction
from orbs.base import Orb
from utils.combat import resolve_target
from utils.dynamic_values import resolve_orb_damage
from utils.types import TargetType


class LightningOrb(Orb):
    passive_timing = "turn_end"
    target_type = TargetType.ENEMY_RANDOM

    def __init__(self):
        self.passive_damage = 3
        self.evoke_damage = 8

    def _resolve_enemy(self):
        targets = resolve_target(self.target_type)
        return targets[0] if targets else None

    def on_passive(self) -> List[Action]:
        target = self._resolve_enemy()
        if target is None:
            return []
        return [
            DealDamageAction(
                damage=resolve_orb_damage(self.passive_damage, target),
                target=target,
                damage_type="magic",
            )
        ]

    def on_evoke(self) -> List[Action]:
        target = self._resolve_enemy()
        if target is None:
            return []
        return [
            DealDamageAction(
                damage=resolve_orb_damage(self.evoke_damage, target),
                target=target,
                damage_type="magic",
            )
        ]
