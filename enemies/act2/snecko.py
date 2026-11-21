"""
Snecko - Normal enemy (Act 2)
Snake enemy that confuses the player.
"""
from engine.random_streams import get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.snecko_intentions import (
    PerplexingGlareIntention, BiteIntention, TailWhipIntention
)


class Snecko(Enemy):
    """Snecko - Snake enemy that confuses the player."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        super().__init__(hp_range=(120, 125) if self.ascension >= 7 else (114, 120))
        
        # Register intentions
        self.add_intention(PerplexingGlareIntention(self))
        self.add_intention(BiteIntention(self))
        self.add_intention(TailWhipIntention(self))
        if self.ascension >= 2:
            self.intentions["bite"].base_damage = 18
            self.intentions["tail_whip"].base_damage = 10
    
    def determine_next_intention(self, floor: int = 1):
        roll = get_rng("ai").randint(0, 99)
        if not self.history_intentions:
            return self.intentions["perplexing_glare"]
        tail_whip = roll < 40 or self.history_intentions[-2:] == ["bite", "bite"]
        return self.intentions["tail_whip" if tail_whip else "bite"]
