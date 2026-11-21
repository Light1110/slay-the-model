"""Acid slime enemies and their move selection."""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.acid_slime_intentions import (
    CorrosiveSpitIntention,
    LickIntention,
    TackleIntention,
    SplitIntention,
)


def _acid_slime_move(history: list[str], *, large: bool) -> str:
    from engine.game_state import game_state

    rng = cast(StreamRandom, get_rng("ai"))
    roll = rng.randint(0, 99)
    last = history[-1] if history else None
    repeated = len(history) >= 2 and history[-2] == last
    high_ascension = game_state.ascension >= 17
    spit_cutoff = 40 if high_ascension else 30
    tackle_cutoff = 80 if high_ascension and not large else 70
    if roll < spit_cutoff:
        if last == "corrosive_spit" and repeated:
            chance = 0.6 if high_ascension and large else None
            return "tackle" if rng.random_boolean(chance) else "lick"
        return "corrosive_spit"
    if roll < tackle_cutoff:
        if last == "tackle" and (not high_ascension or repeated):
            chance = (0.6 if large else 0.5) if high_ascension else 0.4
            return "corrosive_spit" if rng.random_boolean(chance) else "lick"
        return "tackle"
    if last == "lick" and (high_ascension or repeated):
        return "corrosive_spit" if rng.random_boolean(0.4) else "tackle"
    return "lick"


class AcidSlimeL(Enemy):
    """Acid Slime (L) - Large variant that can split at 50% HP."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self, max_hp: int | None = None):
        from engine.game_state import game_state

        super().__init__(
            hp_range=(68, 72) if game_state.ascension >= 7 else (65, 69),
            max_hp=max_hp,
        )
        
        # Register intentions
        self.add_intention(CorrosiveSpitIntention(self))
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
        self.add_intention(SplitIntention(self))
        
        # Track if split has been triggered
        self._split_triggered = False
    
    def determine_next_intention(self, floor: int = 1):
        if self._split_triggered or self.hp <= self.max_hp / 2:
            return self.intentions["split"]
        return self.intentions[_acid_slime_move(self.history_intentions, large=True)]

    def on_any_hp_lost(self, amount: int, source=None, card=None) -> None:
        """Check for split condition when taking damage."""
        if 0 < self.hp <= self.max_hp / 2 and not self._split_triggered:
            self._split_triggered = True
            self.current_intention = self.intentions["split"]


class AcidSlimeM(Enemy):
    """Acid Slime (M) - Medium variant, cannot split."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self, max_hp: int | None = None):
        from engine.game_state import game_state

        super().__init__(
            hp_range=(29, 34) if game_state.ascension >= 7 else (28, 32),
            max_hp=max_hp,
        )
        
        # Register intentions
        self.add_intention(CorrosiveSpitIntention(self))
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        return self.intentions[_acid_slime_move(self.history_intentions, large=False)]


class AcidSlimeS(Enemy):
    """Acid Slime (S) - Small variant."""
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        super().__init__(
            hp_range=(9, 13) if game_state.ascension >= 7 else (8, 12),
        )
        
        # Register intentions
        self.add_intention(LickIntention(self))
        self.add_intention(TackleIntention(self))
    
    def determine_next_intention(self, floor: int = 1):
        if self.history_intentions:
            move = "tackle" if self.history_intentions[-1] == "lick" else "lick"
        else:
            from engine.game_state import game_state

            rng = cast(StreamRandom, get_rng("ai"))
            rng.randint(0, 99)
            move = "tackle" if game_state.ascension < 17 and rng.random_boolean() else "lick"
        return self.intentions[move]
