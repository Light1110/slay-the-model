"""
Snake Plant - Normal enemy (Act 2)
Plant enemy with debuff attacks.
"""
from engine.random_streams import get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.snake_plant_intentions import (
    ChompChompIntention, EnfeeblingSporesIntention
)


class SnakePlant(Enemy):
    """Snake Plant - Plant enemy with debuff attacks."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(75, 79) # todo: 78-82 a7
        )
        
        # Register intentions
        self.add_intention(ChompChompIntention(self))
        self.add_intention(EnfeeblingSporesIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        from powers.definitions.malleable import MalleablePower

        super().on_combat_start(floor)
        self.add_power(MalleablePower(amount=3, owner=self))
    
    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if roll < 65:
            use_spores = history[-2:] == ["chomp_chomp", "chomp_chomp"]
        else:
            cooldown = 2 if game_state.ascension >= 17 else 1
            use_spores = "enfeebling_spores" not in history[-cooldown:]
        return self.intentions["enfeebling_spores" if use_spores else "chomp_chomp"]
