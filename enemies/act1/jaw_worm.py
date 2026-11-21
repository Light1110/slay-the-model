"""
Jaw Worm - Common enemy
Quick attacks with moderate damage.

Act 3 Hard Mode (Jaw Worm Horde):
- Gains Strength and Block at combat start
- Strength: 3 (A2+: 4, A17+: 5)
- Block: 6 (A17+: 9)
"""
from typing import cast

from engine.random_streams import StreamRandom, get_rng
from enemies.base import Enemy
from utils.types import EnemyType
from enemies.act1.jaw_worm_intentions import ChompIntention, BellowIntention, ThrashIntention


class JawWorm(Enemy):
    """Jaw Worm - Quick attacks with moderate damage
    
    Args:
        is_hard: If True, gains Strength and Block at combat start (Act 3 version)
    """
    
    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True
    
    def __init__(self, is_hard: bool = False):
        super().__init__(
            hp_range=(40, 44) # todo: 42-46 a7
        )
        self.is_hard = is_hard
        
        # Register intentions
        self.add_intention(ChompIntention(self))
        self.add_intention(BellowIntention(self))
        self.add_intention(ThrashIntention(self))

    def on_combat_start(self, floor: int = 1) -> None:
        """Apply hard mode buffs if applicable."""
        super().on_combat_start(floor)
        
        if self.is_hard:
            from engine.game_state import game_state
            from powers.definitions.strength import StrengthPower
            
            # Apply Strength based on ascension
            if game_state.ascension >= 17:
                strength = 5
                block = 9
            elif game_state.ascension >= 2:
                strength = 4
                block = 6
            else:
                strength = 3
                block = 6
            
            self.add_power(StrengthPower(amount=strength, owner=self))
            self.gain_block(block)
    
    def determine_next_intention(self, floor: int = 1):
        rng = cast(StreamRandom, get_rng("ai"))
        roll = rng.randint(0, 99)
        history = self.history_intentions
        if not history and not self.is_hard:
            return self.intentions["chomp"]

        last = history[-1] if history else None
        if roll < 25:
            move = "chomp"
            if last == "chomp":
                move = "bellow" if rng.random_boolean(0.5625) else "thrash"
        elif roll < 55:
            move = "thrash"
            if history[-2:] == ["thrash", "thrash"]:
                move = "chomp" if rng.random_boolean(0.357) else "bellow"
        else:
            move = "bellow"
            if last == "bellow":
                move = "chomp" if rng.random_boolean(0.416) else "thrash"
        return self.intentions[move]
