"""
The Guardian - Act 1 Boss
Has Mode Shift and Sharp Hide mechanics.
"""
from engine.runtime_api import add_action, add_actions
from typing import List, TYPE_CHECKING
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.the_guardian_intentions import (
    ChargingUpIntention,
    FierceBashIntention,
    VentSteamIntention,
    WhirlwindIntention,
    DefensiveModeIntention,
    RollAttackIntention,
    TwinSlamIntention
)

if TYPE_CHECKING:
    from actions.base import Action


class TheGuardian(Enemy):
    """The Guardian - Act 1 Boss with Mode Shift and Sharp Hide."""
    
    enemy_type = EnemyType.BOSS
    roll_fixed_opening_intention = True
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = game_state.ascension
        hp = 250 if ascension >= 9 else 240
        super().__init__(hp_range=(hp, hp))
        
        # Register intentions
        self.add_intention(ChargingUpIntention(self))
        self.add_intention(FierceBashIntention(self))
        self.add_intention(VentSteamIntention(self))
        self.add_intention(WhirlwindIntention(self))
        self.add_intention(DefensiveModeIntention(self))
        self.add_intention(RollAttackIntention(self))
        self.add_intention(TwinSlamIntention(self))
        
        # Mode Shift: After losing X HP, switch to Defensive Mode
        self._mode_shift_threshold = 40 if ascension >= 19 else 35 if ascension >= 9 else 30
        self._damage_taken_since_last_shift = 0
        self._in_defensive_mode = False
        
        # Pattern tracking
        self._pattern_index = 0
        self._defensive_pattern_index = 0
    
    def determine_next_intention(self, floor: int = 1):
        """Determine next intention based on mode and pattern.
        
        Main pattern: Charging Up -> Fierce Bash -> Vent Steam -> Whirlwind
        After Mode Shift: Defensive Mode -> Roll Attack -> Twin Slam -> Whirlwind
        """
        # Check if in defensive mode
        if self._in_defensive_mode:
            if self._defensive_pattern_index == 1:
                self._defensive_pattern_index = 2
                return self.intentions["roll_attack"]
            elif self._defensive_pattern_index == 2:
                self._defensive_pattern_index = 3
                return self.intentions["twin_slam"]
            else:
                # Exit defensive mode, reset to main pattern
                self._in_defensive_mode = False
                self._pattern_index = 0
                return self.intentions["whirlwind"]
        
        # Main pattern
        pattern = ["charging_up", "fierce_bash", "vent_steam", "whirlwind"]
        intention_name = pattern[self._pattern_index % len(pattern)]
        self._pattern_index += 1
        
        return self.intentions[intention_name]
    
    def on_any_hp_lost(self, amount: int, source=None, card=None) -> None:
        if self.is_dead() or self._in_defensive_mode:
            return
        self._damage_taken_since_last_shift += amount
        if self._damage_taken_since_last_shift >= self._mode_shift_threshold:
            self._trigger_mode_shift()

    def _trigger_mode_shift(self) -> None:
        self._in_defensive_mode = True
        self._defensive_pattern_index = 1
        self._damage_taken_since_last_shift = 0
        self._mode_shift_threshold += 10
        self.current_intention = self.intentions["defensive_mode"]
        self.gain_block(20)
