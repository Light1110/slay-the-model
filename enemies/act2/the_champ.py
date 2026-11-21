"""The Champ - Act 2 Boss enemy."""
from engine.random_streams import get_rng

from typing import List

from enemies.act2.the_champ_intentions import (
    Anger, DefensiveStance, Execute, FaceSlap, Gloat, HeavySlash, Taunt
)
from enemies.base import Enemy
from utils.types import EnemyType


class TheChamp(Enemy):
    """Boss enemy found at the end of Act 2.
    
    Two-phase boss:
    Phase 1 (HP > 50%): Uses Taunt every 4 turns, 
                        random moves on other turns.
    Phase 2 (HP <= 50%): Uses Anger, then Execute,
                         then pattern: Random, Random, Execute.
    
    Ascension modifiers:
    - A4+: Higher damage on Heavy Slash and Face Slap
    - A9+: Higher HP (320)
    - A19: Gloat replaced with Defensive Stance (with exception)
    """
    
    enemy_type = EnemyType.BOSS
    select_intention_after_enemy_turn = True
    
    def __init__(self, ascension: int | None = None):
        """Initialize The Champ.
        
        Args:
            ascension: Current ascension level
        """
        if ascension is None:
            from engine.game_state import game_state

            ascension = game_state.ascension
        if ascension >= 9:
            hp_max = 440
        else:
            hp_max = 420
        super().__init__(hp_range=(hp_max, hp_max))
        
        self._ascension = ascension
        self._turn_count = 0
        self._phase = 1
        self._stances_selected = 0

        # Register intentions
        self._register_intentions()
    
    def _register_intentions(self) -> None:
        """Register and configure all intentions."""
        heavy_slash = HeavySlash(self)
        face_slap = FaceSlap(self)
        defensive_stance = DefensiveStance(self)
        gloat = Gloat(self)
        taunt = Taunt(self)
        anger = Anger(self)
        execute = Execute(self)
        
        # Apply ascension modifiers
        if self._ascension >= 4:
            heavy_slash.base_damage = 18
            face_slap.base_damage = 14
            gloat.base_strength_gain = 3
            anger.base_strength_gain = 9
        
        if self._ascension >= 9:
            defensive_stance.base_block = 18
            defensive_stance.base_metallicize = 6
        
        if self._ascension >= 19:
            defensive_stance.base_block = 20
            defensive_stance.base_metallicize = 7
            gloat.base_strength_gain = 4
            anger.base_strength_gain = 12
        
        self.add_intention(heavy_slash)
        self.add_intention(face_slap)
        self.add_intention(defensive_stance)
        self.add_intention(gloat)
        self.add_intention(taunt)
        self.add_intention(anger)
        self.add_intention(execute)
    
    def on_combat_start(self, floor: int) -> None:
        self._turn_count = 0
        self._phase = 1
        self._stances_selected = 0
        super().on_combat_start(floor)

    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        self._turn_count += 1
        history = self.history_intentions
        last = history[-1] if history else None
        stance_cutoff = 30 if self._ascension >= 19 else 15
        if self._phase == 1 and self.hp < self.max_hp // 2:
            self._phase = 2
            move = "Anger"
        elif self._phase == 2 and "Execute" not in history[-2:]:
            move = "Execute"
        elif self._phase == 1 and self._turn_count == 4:
            self._turn_count = 0
            move = "Taunt"
        elif last != "Defensive Stance" and self._stances_selected < 2 and roll <= stance_cutoff:
            self._stances_selected += 1
            move = "Defensive Stance"
        elif last not in {"Gloat", "Defensive Stance"} and roll <= 30:
            move = "Gloat"
        elif last != "Face Slap" and roll <= 55:
            move = "Face Slap"
        else:
            move = "Face Slap" if last == "Heavy Slash" else "Heavy Slash"
        return self.intentions[move]
