"""Time Eater - Act 3 Boss."""
from typing import cast

from engine.random_streams import StreamRandom, get_rng

from enemies.act3.time_eater_intentions import (
    Reverberate,
    HeadSlam,
    Ripple,
    Haste,
)
from enemies.base import Enemy
from utils.types import EnemyType


class TimeEater(Enemy):
    """Time Eater is a Boss found at the end of Act 3.
    
    Pattern:
    - Starts with Time Warp power (whenever player plays 12 cards, 
      ends their turn and Time Eater gains 1 Strength)
    - Use Haste when reduced to below half HP (only once per combat)
    - Reverberate (45%), HeadSlam (35%), Ripple (20%)
    - No Reverberate 3x in a row, no HeadSlam/Ripple 2x in a row
    """
    
    enemy_type = EnemyType.BOSS
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        super().__init__(hp_range=(480, 480) if ascension >= 9 else (456, 456))
        self.add_intention(Reverberate(self))
        self.add_intention(HeadSlam(self))
        self.add_intention(Ripple(self))
        self.add_intention(Haste(self))
        
        self._haste_used = False
    
    def on_combat_start(self, floor: int):
        """Initialize combat state and add Time Warp power."""
        self._haste_used = False
        super().on_combat_start(floor)
        
        # Add Time Warp power at combat start
        from powers.definitions.time_warp import TimeWarpPower
        self.add_power(TimeWarpPower(amount=1, owner=self))
    
    def determine_next_intention(self, floor: int):
        rng = cast(StreamRandom, get_rng("ai"))
        roll = rng.randint(0, 99)
        if not self._haste_used and self.hp < self.max_hp // 2:
            self._haste_used = True
            return self.intentions["Haste"]

        history = self.history_intentions
        last = history[-1] if history else None
        while True:
            if roll < 45:
                if history[-2:] != ["Reverberate", "Reverberate"]:
                    return self.intentions["Reverberate"]
                roll = rng.randint(50, 99)
            elif roll < 80:
                if last != "Head Slam":
                    return self.intentions["Head Slam"]
                move = "Reverberate" if rng.random_boolean(0.66) else "Ripple"
                return self.intentions[move]
            elif last != "Ripple":
                return self.intentions["Ripple"]
            else:
                roll = rng.randint(0, 74)
