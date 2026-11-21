"""
Chosen - Normal enemy (Act 2)
Cultist with hex and drain abilities.
"""
from engine.random_streams import get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.chosen_intentions import (
    PokeIntention, HexIntention, DebilitateIntention, DrainIntention, ZapIntention
)


class Chosen(Enemy):
    """Chosen - Cultist enemy with hex and drain abilities."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(95, 99) # todo: 98-103 a7
        )
        
        # Register intentions
        self.add_intention(PokeIntention(self))
        self.add_intention(HexIntention(self))
        self.add_intention(DebilitateIntention(self))
        self.add_intention(DrainIntention(self))
        self.add_intention(ZapIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if not history:
            move = "hex" if game_state.ascension >= 17 else "poke"
        elif len(history) == 1 and history[-1] == "poke":
            move = "hex"
        elif history[-1] in {"debilitate", "drain"}:
            move = "zap" if roll < 40 else "poke"
        else:
            move = "debilitate" if roll < 50 else "drain"
        return self.intentions[move]
