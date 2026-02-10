"""
Ironclad Basic card - Bash
"""

from typing import List
from actions.base import Action
from actions.combat import AttackAction
from cards.base import Card
from entities.creature import Creature
from utils.registry import register
from utils.types import CardType, RarityType


@register("card")
class Bash(Card):
    """Deal damage and apply Vulnerable"""

    card_type = CardType.ATTACK
    rarity = RarityType.STARTER

    base_cost = 2
    base_damage = 8
    base_magic = {"vulnerable": 2}

    upgrade_damage = 10
    upgrade_magic = {"vulnerable": 3}

    def on_play(self, target: Creature | None = None) -> List[Action]:
        return super().on_play(target) + [
            # todo: ApplyPowerAction
        ]
