"""Corrupt Heart - Act 4 Final Boss."""
from typing import cast

from engine.random_streams import StreamRandom, get_rng

from enemies.act4.corrupt_heart_intentions import (
    BloodShots,
    BuffHeart,
    Debilitate,
    Echo,
)
from enemies.base import Enemy
from powers.definitions.beat_of_death import BeatOfDeathPower
from powers.definitions.invincible import InvinciblePower
from utils.types import EnemyType


class CorruptHeart(Enemy):
    """Corrupt Heart is the final boss of the Spire (Act 4).

    Pattern:
    - Turn 1: Debilitate
    - From Turn 4, every 3 turns: Buff
    - Other turns: 50/50 pair order of Blood Shots and Echo
    """
    
    enemy_type = EnemyType.BOSS
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        hp = 800 if ascension >= 9 else 750
        super().__init__(hp_range=(hp, hp))
        self.add_intention(Debilitate(self))
        self.add_intention(BloodShots(self))
        self.add_intention(Echo(self))
        self.add_intention(BuffHeart(self))

        self._buff_count = 0
    
    def on_combat_start(self, floor: int):
        """Initialize combat state."""
        from engine.game_state import game_state

        ascension = getattr(game_state, "ascension", 0)
        self._buff_count = 0
        super().on_combat_start(floor)
        self.remove_power("Beat of Death")
        self.remove_power("Invincible")
        self.remove_power("Painful Stabs")
        self.add_power(InvinciblePower(amount=200 if ascension >= 19 else 300, owner=self))
        self.add_power(BeatOfDeathPower(amount=2 if ascension >= 19 else 1, owner=self))
    
    def determine_next_intention(self, floor: int) -> str:
        rng = cast(StreamRandom, get_rng("ai"))
        rng.randint(0, 99)
        completed = len(self.history_intentions)
        if completed == 0:
            return "Debilitate"

        phase = (completed - 1) % 3
        if phase == 0:
            return "Blood Shots" if rng.random_boolean() else "Echo"
        if phase == 1:
            return "Blood Shots" if self.history_intentions[-1] == "Echo" else "Echo"
        return "Buff"
