"""
Mystic - Normal enemy (Act 2)
Support caster that heals and buffs allies.
"""
from engine.random_streams import get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.mystic_intentions import (
    AttackIntention, BuffIntention, HealIntention
)


class Mystic(Enemy):
    """Mystic - Support caster enemy."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(48, 56) # todo: 50-58 a7
        )
        
        # Register intentions
        self.add_intention(AttackIntention(self))
        self.add_intention(BuffIntention(self))
        self.add_intention(HealIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        combat = game_state.current_combat
        allies = combat.enemies if combat is not None else [self]
        missing_hp = sum(enemy.max_hp - enemy.hp for enemy in allies if enemy.is_alive)
        high_ascension = game_state.ascension >= 17
        if missing_hp > (20 if high_ascension else 15) and history[-2:] != ["heal", "heal"]:
            return self.intentions["heal"]
        attack_limit = 1 if high_ascension else 2
        if roll >= 40 and history[-attack_limit:] != ["attack"] * attack_limit:
            return self.intentions["attack"]
        return self.intentions["attack" if history[-2:] == ["buff", "buff"] else "buff"]
