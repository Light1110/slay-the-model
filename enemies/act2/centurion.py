"""
Centurion - Normal enemy (Act 2)
Warrior that protects the Mystic.
"""
from engine.random_streams import get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.centurion_intentions import (
    SlashIntention, ProtectIntention, FuryIntention
)


class Centurion(Enemy):
    """Centurion - Warrior enemy that protects Mystic."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(
            hp_range=(76, 80) # todo: 78-83 a7
        )
        
        # Register intentions
        self.add_intention(SlashIntention(self))
        self.add_intention(ProtectIntention(self))
        self.add_intention(FuryIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        recent = self.history_intentions[-2:]
        may_support = recent not in (["protect", "protect"], ["fury", "fury"])
        if not (roll >= 65 and may_support) and recent != ["slash", "slash"]:
            return self.intentions["slash"]
        combat = game_state.current_combat
        has_ally = combat is not None and any(
            enemy is not self and enemy.is_alive for enemy in combat.enemies
        )
        return self.intentions["protect" if has_ally else "fury"]
