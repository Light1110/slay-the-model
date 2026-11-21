"""Reptomancer enemy intentions for Slay the Model."""
from engine.runtime_api import add_action, add_actions

import random
from typing import List

from actions.combat import AttackAction, ApplyPowerAction, AddEnemyAction
from enemies.act3.dagger import Dagger
from enemies.intention import Intention
from powers.definitions.weak import WeakPower

DAGGER_POSITIONS = (210, -220, 180, -250)


class SpawnDaggerIntention(Intention):
    """Reptomancer Spawn Dagger intention - summons a Dagger."""
    
    def __init__(self, enemy):
        super().__init__("Spawn Dagger", enemy)
    
    def execute(self) -> None:
        """Execute Spawn Dagger intention."""
        from engine.game_state import game_state
        combat = game_state.current_combat
        if combat is None:
            return
        
        positions = combat.open_formation_positions(DAGGER_POSITIONS)[:self.enemy.daggers_per_spawn]
        add_actions([AddEnemyAction(Dagger(), position=position) for position in positions])


class BigBiteIntention(Intention):
    """Reptomancer's single-hit attack."""
    
    def __init__(self, enemy):
        from engine.game_state import game_state

        super().__init__("Big Bite", enemy)
        self.base_damage = 34 if game_state.ascension >= 3 else 30
    
    def execute(self) -> None:
        """Execute Big Bite intention."""
        from engine.game_state import game_state
        
        from engine.game_state import game_state
        add_actions(
        [AttackAction(
            self.base_damage,
            game_state.player,
            self.enemy,
            "attack"
        )]
        )


class SnakeStrikeIntention(Intention):
    """Reptomancer's two-hit attack that applies Weak."""
    
    def __init__(self, enemy):
        from engine.game_state import game_state

        super().__init__("Snake Strike", enemy)
        self.base_damage = 16 if game_state.ascension >= 3 else 13
        self.base_times = 2
    
    def execute(self) -> None:
        """Execute Snake Strike intention."""
        from engine.game_state import game_state
        
        actions = []
        for _ in range(self.base_times):
            actions.append(AttackAction(
                self.base_damage,
                game_state.player,
                self.enemy,
                "attack"
            ))
        actions.append(ApplyPowerAction(
            WeakPower(duration=1, owner=game_state.player),
            game_state.player,
            source=self.enemy,
        ))
        add_actions(actions)
