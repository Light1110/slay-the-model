"""Spire Growth enemy for Slay the Model."""
from engine.random_streams import get_rng

from typing import List, Optional

from enemies.act3.spire_growth_intentions import Constrict, QuickTackle, Smash
from enemies.base import Enemy
from utils.types import EnemyType


class SpireGrowth(Enemy):
    """Spire Growth is a normal Enemy found exclusively in Act 3.
    
    Special mechanics:
    - Uses Constrict to apply damage over time
    - Uses Smash if player already has Constricted
    """
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        super().__init__(hp_range=(170, 170)) # todo: 190 a7
        
        # Register intentions
        self.add_intention(Constrict(self))
        self.add_intention(QuickTackle(self))
        self.add_intention(Smash(self))
    
    def determine_next_intention(self, floor: int):
        from engine.game_state import game_state

        roll = get_rng("ai").randint(0, 99)
        history = self.history_intentions
        can_constrict = not self._player_has_constricted() and history[-1:] != ["Constrict"]
        if game_state.ascension >= 17 and can_constrict:
            move = "Constrict"
        elif roll < 50 and history[-2:] != ["Quick Tackle", "Quick Tackle"]:
            move = "Quick Tackle"
        elif can_constrict:
            move = "Constrict"
        elif history[-2:] != ["Smash", "Smash"]:
            move = "Smash"
        else:
            move = "Quick Tackle"
        return self.intentions[move]

    def _player_has_constricted(self) -> bool:
        """Check if player has Constricted power."""
        from engine.game_state import game_state
        return game_state.player is not None and game_state.player.has_power("Constricted")
