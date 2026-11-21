"""Reptomancer enemy for Slay the Model."""
from engine.random_streams import get_rng

from enemies.act3.reptomancer_intentions import (
    SpawnDaggerIntention, BigBiteIntention, SnakeStrikeIntention
)
from enemies.act3.dagger import Dagger
from enemies.base import Enemy
from utils.types import EnemyType


class Reptomancer(Enemy):
    """Reptomancer is an elite enemy found exclusively in Act 3.
    
    Special mechanics:
    - Summons Daggers that deal damage and explode
    - Always starts with Spawn Dagger
    - Cannot have more than 4 Daggers in play
    """
    
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = game_state.ascension
        # The constructor samples its base HP before applying the ascension range.
        get_rng("monster_hp").randint(180, 190)
        super().__init__(hp_range=(190, 200) if ascension >= 8 else (180, 190))
        self.daggers_per_spawn = 2 if ascension >= 18 else 1
        
        # Register intentions
        self.add_intention(SpawnDaggerIntention(self))
        self.add_intention(BigBiteIntention(self))
        self.add_intention(SnakeStrikeIntention(self))
    
    def determine_next_intention(self, floor: int):
        from engine.game_state import game_state

        rng = get_rng("ai")
        roll = rng.randint(0, 99)
        history = self.history_intentions
        if not history:
            return self.intentions["Spawn Dagger"]

        combat = game_state.current_combat
        allies = sum(enemy is not self and enemy.is_alive for enemy in combat.enemies) if combat else 0
        last = history[-1]
        can_spawn = allies < 4 and history[-2:] != ["Spawn Dagger", "Spawn Dagger"]
        while True:
            if roll < 33:
                if last != "Snake Strike":
                    return self.intentions["Snake Strike"]
                roll = rng.randint(33, 99)
            elif roll < 66:
                return self.intentions["Spawn Dagger" if can_spawn else "Snake Strike"]
            elif last != "Big Bite":
                return self.intentions["Big Bite"]
            else:
                roll = rng.randint(0, 65)

    def on_death(self) -> None:
        from actions.combat import RemoveEnemyAction
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        super().on_death()
        combat = game_state.current_combat
        if combat is not None:
            add_actions([
                RemoveEnemyAction(enemy) for enemy in combat.enemies
                if isinstance(enemy, Dagger) and enemy.is_alive
            ])
