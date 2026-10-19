"""Transient enemy for Slay the Model."""

from enemies.act3.transient_intentions import TransientAttack
from enemies.base import Enemy
from powers.definitions.fading import FadingPower
from powers.definitions.shifting import ShiftingPower
from utils.types import EnemyType


class Transient(Enemy):
    """Transient is a normal Enemy found exclusively in Act 3.

    Special mechanics:
    - Damage scales with turn number: 30 (40 on A2+) + 10 per completed attack
    - Becomes more dangerous the longer the fight goes
    """

    enemy_type = EnemyType.NORMAL

    def __init__(self):
        super().__init__(hp_range=(999, 999))
        self._attacks_executed = 0

        # Register intentions
        self.add_intention(TransientAttack(self))

    def on_combat_start(self, floor: int = 1) -> None:
        """Apply Transient combat-start powers."""
        from engine.game_state import game_state

        self._attacks_executed = 0
        super().on_combat_start(floor)

        fading_turns = 6 if game_state.ascension >= 17 else 5
        self.add_power(FadingPower(duration=fading_turns, owner=self))
        self.add_power(ShiftingPower(owner=self))

    def determine_next_intention(self, floor: int = 1):
        return self.intentions["Attack"]
