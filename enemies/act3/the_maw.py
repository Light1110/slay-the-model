"""The Maw enemy for Slay the Model."""
from engine.random_streams import get_rng

from enemies.act3.the_maw_intentions import (
    TheMawRoar, TheMawSlam, TheMawNomNom, TheMawDrool
)
from enemies.base import Enemy
from utils.types import EnemyType


class TheMaw(Enemy):
    """The Maw is a normal Enemy found exclusively in Act 3.

    Special mechanics:
    - Always starts with Roar (applies 3 Weak and 3 Frail)
    - Afterwards has 50/50 chance of Slam or Nom Nom
    - After Drool: 50/50 between Slam and Nom Nom
    - After Nom Nom: Drool
    - After Slam: 50/50 between Nom Nom and Drool
    - 300 HP
    """

    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True

    def __init__(self):
        super().__init__(max_hp=300)
        self._turn_count = 0
        self._last_move = None
        self._selected_after_turn = -1

        # Register intentions
        self._roar = TheMawRoar(self)
        self._slam = TheMawSlam(self)
        self._nom_nom = TheMawNomNom(self)
        self._drool = TheMawDrool(self)

        self.add_intention(self._roar)
        self.add_intention(self._slam)
        self.add_intention(self._nom_nom)
        self.add_intention(self._drool)

    def on_combat_start(self, floor: int = 1) -> None:
        self._selected_after_turn = -1
        self._last_move = None
        super().on_combat_start(floor)

    def determine_next_intention(self, floor: int = 1):
        """Select once per executed turn, preserving the existing move probabilities."""
        completed = len(self.history_intentions)
        if self._selected_after_turn == completed:
            return self.intentions[self._last_move]
        self._selected_after_turn = completed
        self._turn_count = completed + 1
        # Original turnCount starts at 1 and advances before the opening Roar.
        self._nom_nom._hits = (completed + 2) // 2
        last = self.history_intentions[-1] if self.history_intentions else None
        roll = get_rng("ai").randint(0, 99)
        if last is None:
            selected = "Roar"
        elif roll < 50 and last != "Nom Nom":
            selected = "Nom Nom"
        elif last in {"Slam", "Nom Nom"}:
            selected = "Drool"
        else:
            selected = "Slam"
        self._last_move = selected
        return self.intentions[selected]
