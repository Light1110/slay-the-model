"""Giant Head Elite intentions for Act 3."""
from engine.runtime_api import add_action, add_actions

import random
from typing import List

from actions.combat import (
    AttackAction,
    ApplyPowerAction,
)
from enemies.intention import Intention


class CountIntention(Intention):
    """Deals 13 damage."""
    
    def __init__(self, enemy):
        super().__init__("Count", enemy)
        self.base_damage = 13
    
    def execute(self) -> None:
        """Execute the intention."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [AttackAction(
            damage=self.base_damage,
            target=game_state.player,
            source=self.enemy,
            damage_type="attack"
        )]
        )


class GlareIntention(Intention):
    """Applies 1 Weak."""
    
    def __init__(self, enemy):
        super().__init__("Glare", enemy)
        self.base_amount = 1
    
    def execute(self) -> None:
        """Execute the intention."""
        from engine.game_state import game_state
        from engine.game_state import game_state
        add_actions(
        [ApplyPowerAction(
            power="weak",
            target=game_state.player,
            amount=self.base_amount,
            duration=1
        )]
        )


class ItIsTimeIntention(Intention):
    """Gain 5 base damage per use, up to 60 (70 on A3+)."""

    def __init__(self, enemy):
        super().__init__("It Is Time", enemy)
        from engine.game_state import game_state

        self.base_damage = 40 if game_state.ascension >= 3 else 30
        self.max_damage = self.base_damage + 30

    def get_base_damage(self) -> int:
        return min(self.base_damage + 5 * self.enemy._it_is_time_count, self.max_damage)

    def execute(self) -> None:
        from engine.game_state import game_state

        damage = self.get_base_damage()
        add_actions([AttackAction(damage, game_state.player, self.enemy, "attack")])
        self.enemy._it_is_time_count += 1
