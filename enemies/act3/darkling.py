"""Darkling enemy for Slay the Model."""
from engine.random_streams import get_rng

from enemies.act3.darkling_intentions import (
    Chomp,
    Harden,
    Nip,
    Reincarnate,
    Regrowing,
)
from enemies.base import Enemy
from powers.definitions.life_link import LifeLinkPower
from utils.types import EnemyType


class Darkling(Enemy):
    """Darkling is a normal Enemy found exclusively in Act 3.

    Special mechanics:
    - When HP reaches 0, becomes untargetable and uses Regrowing
    - Next turn uses Reincarnate to revive with 50% HP
    """

    enemy_type = EnemyType.NORMAL
    select_intention_after_enemy_turn = True

    def __init__(self):
        super().__init__(hp_range=(50, 56))
        self._first_move = True
        self._is_regrowing = False

        # Register intentions
        self.add_intention(Harden(self))
        self.add_intention(Nip(self))
        self.add_intention(Chomp(self))
        self.add_intention(Regrowing(self))
        self.add_intention(Reincarnate(self))

    def on_combat_start(self, floor: int = 1) -> None:
        """Initialize Darkling combat state."""
        super().on_combat_start(floor)
        self.add_power(LifeLinkPower(owner=self))

    def determine_next_intention(self, floor: int):
        from engine.game_state import game_state

        rng = get_rng("ai")
        roll = rng.randint(0, 99)
        if self._is_regrowing:
            return self.intentions["Reincarnate"]
        if self._first_move:
            self._first_move = False
            return self.intentions["Harden" if roll < 50 else "Nip"]

        combat = game_state.current_combat
        enemies = combat.enemies if combat is not None else []
        can_chomp = self not in enemies or enemies.index(self) % 2 == 0
        history = self.history_intentions
        while True:
            if roll < 40:
                if can_chomp and history[-1:] != ["Chomp"]:
                    return self.intentions["Chomp"]
                roll = rng.randint(40, 99)
            elif roll < 70:
                move = "Nip" if history[-1:] == ["Harden"] else "Harden"
                return self.intentions[move]
            elif history[-2:] != ["Nip", "Nip"]:
                return self.intentions["Nip"]
            else:
                roll = rng.randint(0, 99)

    @property
    def half_dead(self) -> bool:
        return self._is_regrowing and self.hp <= 0 and not self.is_dead()

    def on_hp_depleted(self) -> None:
        self._is_regrowing = True
        self.current_intention = self.intentions["Regrowing..."]

    def after_hp_depleted(self) -> None:
        self.powers.clear()
        if self.is_dead():
            from engine.game_state import game_state

            combat = game_state.current_combat
            for enemy in combat.enemies if combat is not None else [self]:
                if isinstance(enemy, Darkling) and enemy.hp <= 0:
                    enemy._is_regrowing = False
                    enemy.current_intention = None
    def is_dead(self) -> bool:
        """Darkling only dies when no other linked enemy is alive."""
        if self.hp > 0:
            return False

        from engine.game_state import game_state

        combat = getattr(game_state, "current_combat", None)
        if not combat:
            return True

        for enemy in combat.enemies:
            if enemy is self:
                continue
            # The Life Link power is cleared on collapse; group membership
            # must survive that cleanup and a subsequent reincarnation.
            if isinstance(enemy, Darkling) and enemy.hp > 0:
                return False
        return True
