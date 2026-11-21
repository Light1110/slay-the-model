"""
Cultist - Common enemy
Quick attacks with weak damage.
"""
from enemies.base import Enemy
from engine.random_streams import get_rng
from utils.types import EnemyType
from enemies.act1.cultist_intentions import CultistRitualIntention, CultistAttackIntention


class Cultist(Enemy):
    """Cultist - Quick attacks with weak damage"""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self, ascension: int | None = None):
        if ascension is None:
            from engine.game_state import game_state

            ascension = game_state.ascension
        super().__init__(hp_range=(50, 56) if ascension >= 7 else (48, 54))
        self.ascension = ascension
        
        # Register intentions
        self.add_intention(CultistRitualIntention(self))
        self.add_intention(CultistAttackIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on history.
        
        Cultist pattern:
        - First turn: Always Ritual
        - After Ritual: Always Attack
        - After Attack: Always Attack
        """
        get_rng("ai").randint(0, 99)

        # First turn: Always Ritual
        if not self.history_intentions:
            return self.intentions["ritual"]
        
        # After first turn: Always Attack
        return self.intentions["attack"]
