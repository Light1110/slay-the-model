"""
Byrd - Normal enemy (Act 2)
Flying bird that uses aerial attacks.
"""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act2.byrd_intentions import (
    PeckIntention, CawIntention, SwoopIntention,
    StunnedIntention, HeadbuttIntention, GoAirborneIntention
)


class Byrd(Enemy):
    """Byrd - Flying bird enemy with aerial attack patterns."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        self.ascension = game_state.ascension
        super().__init__(hp_range=(26, 33) if self.ascension >= 7 else (25, 31))
        self.flight_stacks = 4 if self.ascension >= 17 else 3
        
        # Track flying state
        self._is_flying = True
        self._grounded_pattern_index = 0
        
        # Register intentions
        self.add_intention(PeckIntention(self))
        self.add_intention(CawIntention(self))
        self.add_intention(SwoopIntention(self))
        self.add_intention(StunnedIntention(self))
        self.add_intention(HeadbuttIntention(self))
        self.add_intention(GoAirborneIntention(self))
    
    def on_combat_start(self, floor: int = 1):
        """Initialize combat state."""
        self._is_flying = True
        self._grounded_pattern_index = 0
        from powers.definitions.flying import FlyingPower
        self.add_power(FlyingPower(amount=self.flight_stacks, owner=self))
        # The opening selector reads Flying; initialize it before selecting.
        super().on_combat_start(floor)
    
    def remove_power(self, power_or_name) -> None:
        had_flying = self.has_power("Flying")
        super().remove_power(power_or_name)
        if had_flying and not self.has_power("Flying") and self.is_alive:
            self._is_flying = False
            self._grounded_pattern_index = 1
            self.current_intention = self.intentions["stunned"]

    def determine_next_intention(self, floor: int = 1):
        history = self.history_intentions
        last = history[-1] if history else None
        if last == "headbutt" and not self._is_flying:
            return self.intentions["go_airborne"]

        rng = cast(StreamRandom, get_rng("ai"))
        roll = rng.randint(0, 99)
        if not self._is_flying:
            return self.intentions["headbutt"]
        if last is None:
            return self.intentions["caw" if rng.random_boolean(0.375) else "peck"]
        if roll < 50:
            move = "peck"
            if history[-2:] == ["peck", "peck"]:
                move = "swoop" if rng.random_boolean(0.4) else "caw"
        elif roll < 70:
            move = "swoop"
            if last == "swoop":
                move = "caw" if rng.random_boolean(0.375) else "peck"
        else:
            move = "caw"
            if last == "caw":
                move = "swoop" if rng.random_boolean(0.2857) else "peck"
        return self.intentions[move]
