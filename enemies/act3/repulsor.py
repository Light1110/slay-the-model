"""Repulsor enemy for Slay the Model."""
from engine.random_streams import get_rng

from typing import List, Optional

from enemies.act3.repulsor_intentions import DazeIntention, RepulsorAttack
from enemies.base import Enemy
from utils.types import EnemyType


class Repulsor(Enemy):
    """Repulsor is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Repeatedly gives the player Dazed cards
    - 80% Daze, 20% Attack
    """
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(hp_range=(40, 45))
        
        # Register intentions
        self.add_intention(DazeIntention(self))
        self.add_intention(RepulsorAttack(self))
    
    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        use_attack = roll < 20 and self.history_intentions[-1:] != ["Attack"]
        return self.intentions["Attack" if use_attack else "Daze"]
