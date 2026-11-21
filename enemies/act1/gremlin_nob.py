# -*- coding: utf-8 -*-
"""Gremlin Nob - Act 1 Elite enemy"""
from engine.random_streams import get_rng

from enemies.base import Enemy
from utils.types import EnemyType
from utils.registry import register
from enemies.act1.gremlin_nob_intentions import (
    BellowIntention, SkullBashIntention, BullRushIntention
)


@register("enemy")
class GremlinNob(Enemy):
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self, ascension: int = 0):
        from engine.game_state import game_state

        ascension = max(ascension, getattr(game_state, "ascension", 0))
        if ascension >= 8:
            hp = get_rng("monster_hp").randint(85, 90)
        else:
            hp = get_rng("monster_hp").randint(82, 86)
        
        super().__init__(max_hp=hp)
        self.ascension = ascension
        
        skull_damage = 8 if ascension >= 3 else 6
        bull_damage = 16 if ascension >= 3 else 14
        
        # Register intentions with keys
        self.add_intention(BellowIntention(self))
        self.add_intention(SkullBashIntention(self, skull_damage))
        self.add_intention(BullRushIntention(self, bull_damage))
        
    def determine_next_intention(self, floor: int = 1):
        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        if not history:
            return self.intentions["bellow"]
        if self.ascension >= 18:
            use_skull_bash = "skull_bash" not in history[-2:]
        else:
            use_skull_bash = roll < 33 or history[-2:] == ["bull_rush", "bull_rush"]
        return self.intentions["skull_bash" if use_skull_bash else "bull_rush"]
