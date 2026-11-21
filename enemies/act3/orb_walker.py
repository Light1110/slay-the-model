"""Orb Walker enemy - Act 3 Normal enemy."""
from engine.random_streams import get_rng

from enemies.base import Enemy
from enemies.act3.orb_walker_intentions import Laser, Claw
from utils.types import EnemyType


class OrbWalker(Enemy):
    """Orb Walker is a normal Enemy encountered exclusively in Act 3."""

    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True

    def __init__(self):
        from engine.game_state import game_state

        # The initial HP roll is replaced by a second roll in the constructor.
        get_rng("monster_hp").randint(90, 96)
        super().__init__(hp_range=(92, 102) if game_state.ascension >= 7 else (90, 96))
        self.add_intention(Laser(self))
        self.add_intention(Claw(self))

    def determine_next_intention(self, floor: int):
        roll = get_rng("ai").randint(0, 99)
        recent = self.history_intentions[-2:]
        if roll < 40:
            move = "Laser" if recent == ["Claw", "Claw"] else "Claw"
        else:
            move = "Claw" if recent == ["Laser", "Laser"] else "Laser"
        return self.intentions[move]
