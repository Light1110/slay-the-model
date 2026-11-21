"""Taskmaster - Act 2 Elite enemy."""
from engine.random_streams import get_rng

from typing import List

from enemies.act2.taskmaster_intentions import ScouringWhip
from enemies.base import Enemy
from utils.types import EnemyType


class Taskmaster(Enemy):
    """Elite enemy found in Act 2 (Slavers encounter).
    
    Only uses Scouring Whip attack.
    Found with Red Slaver and Blue Slaver.
    Also found in The Colosseum event with Gremlin Nob.
    """
    
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(hp_range=(48, 54))
        
        # Register intentions
        self.add_intention(ScouringWhip(self))
    
    def determine_next_intention(self, floor: int) -> None:
        """Taskmaster only has one attack."""
        get_rng("ai").randint(0, 99)
        self.current_intention = self.intentions["Scouring Whip"]
