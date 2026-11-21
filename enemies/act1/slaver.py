"""
Slaver enemies - Blue and Red Slaver.
Human enemies with various attacks.
"""
from engine.random_streams import get_rng
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.slaver_intentions import (
    StabIntention,
    RakeIntention,
    ScrapeIntention,
    EntangleIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class BlueSlaver(Enemy):
    """Blue Slaver - Deals damage and applies Weak."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(46, 50) # todo: 48-52 a7
        )
        
        # Register intentions
        self.add_intention(StabIntention(self, damage=12))
        self.add_intention(RakeIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if roll >= 40 and history[-2:] != ["stab", "stab"]:
            return self.intentions["stab"]
        rake_limit = 1 if game_state.ascension >= 17 else 2
        move = "stab" if history[-rake_limit:] == ["rake"] * rake_limit else "rake"
        return self.intentions[move]


class RedSlaver(Enemy):
    """Red Slaver - Deals damage, applies Vulnerable, and can Entangle."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(46, 50) # todo: 48-52 a7
        )
        
        # Register intentions
        self.add_intention(StabIntention(self, damage=13))
        self.add_intention(ScrapeIntention(self))
        self.add_intention(EntangleIntention(self))
        
    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if not history:
            return self.intentions["stab"]
        used_entangle = "entangle" in history
        if roll >= 75 and not used_entangle:
            return self.intentions["entangle"]
        if roll >= 55 and used_entangle and history[-2:] != ["stab", "stab"]:
            return self.intentions["stab"]
        scrape_limit = 1 if game_state.ascension >= 17 else 2
        move = "stab" if history[-scrape_limit:] == ["scrape"] * scrape_limit else "scrape"
        return self.intentions[move]
