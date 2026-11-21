"""Spiker enemy for Slay the Model."""
from engine.random_streams import get_rng

from typing import List, Optional

from enemies.act3.spiker_intentions import BuffThorns, SpikeAttack
from enemies.base import Enemy
from utils.types import EnemyType


class Spiker(Enemy):
    """Spiker is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Focuses on building Thorns to make attacking it dangerous
    - Cannot use Buff Thorns more than 6 times
    """
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(hp_range=(42, 56)) # todo: 44-60 a7
        
        # Register intentions
        self.add_intention(SpikeAttack(self))
        self.add_intention(BuffThorns(self))
    
    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        use_attack = history.count("Buff Thorns") >= 6 or (roll < 50 and history[-1:] != ["Attack"])
        return self.intentions["Attack" if use_attack else "Buff Thorns"]
