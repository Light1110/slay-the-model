"""Silent uncommon skill card - Catalyst."""

from typing import List

from actions.base import Action
from actions.combat import ApplyPowerAction
from cards.base import Card
from engine.runtime_api import add_action
from entities.creature import Creature
from powers.definitions.poison import PoisonPower
from utils.registry import register
from utils.types import CardType, RarityType, TargetType


class MultiplyPoisonAction(Action):
    """Apply extra Poison equal to the target's current Poison times (multiplier - 1)."""

    def __init__(self, target: Creature, multiplier: int):
        self.target = target
        self.multiplier = multiplier

    def execute(self) -> None:
        if self.target is None:
            return
        poison = self.target.get_power("Poison")
        if poison is None or poison.amount <= 0:
            return
        extra = poison.amount * (self.multiplier - 1)
        if extra <= 0:
            return
        add_action(
            ApplyPowerAction(
                PoisonPower(amount=extra, duration=extra, owner=self.target),
                self.target,
            ),
            to_front=True,
        )


@register("card")
class Catalyst(Card):
    """Multiply an enemy's Poison."""

    card_type = CardType.SKILL
    rarity = RarityType.UNCOMMON
    target_type = TargetType.ENEMY_SELECT

    base_cost = 1
    base_exhaust = True
    base_magic = {"multiplier": 2}

    upgrade_magic = {"multiplier": 3}

    def on_play(self, targets: List[Creature] = []):
        target = targets[0] if targets else None
        if target is not None:
            add_action(MultiplyPoisonAction(target, self.get_magic_value("multiplier")))
        super().on_play(targets)
