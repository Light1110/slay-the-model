"""Gremlin Leader - Act 2 Elite enemy."""
from engine.random_streams import get_rng

from typing import List

from enemies.act2.gremlin_leader_intentions import Encourage, Rally, Stab
from enemies.base import Enemy
from utils.types import EnemyType


class GremlinLeader(Enemy):
    """Elite enemy found in Act 2.
    
    Summons Gremlin minions and buffs them.
    Pattern depends on number of Gremlins in battle.
    Cannot use any intent twice in a row.
    No more than 3 small Gremlins can be present.
    """
    
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(hp_range=(140, 148)) # todo: 145-155 a8
        
        # Register intentions
        self.add_intention(Encourage(self))
        self.add_intention(Stab(self))
        self.add_intention(Rally(self))
    
    def determine_next_intention(self, floor: int):
        from engine.game_state import game_state

        combat = game_state.current_combat
        count = sum(enemy is not self and enemy.is_alive for enemy in combat.enemies) if combat else 0
        history = self.history_intentions
        last = history[-1] if history else None
        rng = get_rng("ai")
        roll = rng.randint(0, 99)
        if count == 0:
            use_rally = last == "Stab" or (roll < 75 and last != "Rally!")
            return self.intentions["Rally!" if use_rally else "Stab"]
        if count >= 2:
            use_encourage = last == "Stab" or (roll < 66 and last != "Encourage")
            return self.intentions["Encourage" if use_encourage else "Stab"]

        while True:
            if roll < 50:
                if last != "Rally!":
                    return self.intentions["Rally!"]
                roll = rng.randint(50, 99)
            elif roll < 80:
                return self.intentions["Stab" if last == "Encourage" else "Encourage"]
            elif last != "Stab":
                return self.intentions["Stab"]
            else:
                roll = rng.randint(0, 80)

    def on_death(self) -> None:
        from actions.combat import RemoveEnemyAction
        from engine.game_state import game_state
        from engine.runtime_api import add_actions

        super().on_death()
        combat = game_state.current_combat
        if combat is not None:
            add_actions([
                RemoveEnemyAction(enemy) for enemy in combat.enemies
                if enemy is not self and enemy.is_alive and enemy.is_minion
            ])
