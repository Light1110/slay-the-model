"""Nemesis elite enemy - Act 3 Elite."""
from typing import cast

from engine.random_streams import StreamRandom, get_rng

from enemies.act3.nemesis_intentions import (
    TriAttack,
    TriBurn,
    Scythe,
)
from enemies.base import Enemy
from powers.definitions.intangible import IntangiblePower
from utils.types import EnemyType


class Nemesis(Enemy):
    """Nemesis is an Elite enemy found exclusively in Act 3.
    
    Pattern:
    - First turn: 50% Tri Attack or 50% Tri Burn
    - Afterwards:
      - Tri Burn (35% primary branch)
      - Tri Attack (35% primary branch)
      - Scythe (30% primary branch)
    - Cannot use Tri Burn or Scythe twice in a row
    - Cannot use Tri Attack three times in a row
    """
    
    enemy_type = EnemyType.ELITE
    select_intention_after_enemy_turn = True
    
    def __init__(self):
        from engine.game_state import game_state

        ascension = game_state.ascension
        hp = 200 if ascension >= 8 else 185
        super().__init__(hp_range=(hp, hp))
        self.add_intention(TriAttack(self))
        self.add_intention(TriBurn(self))
        self.add_intention(Scythe(self))
        self.intentions["Tri Attack"].base_damage = 7 if ascension >= 3 else 6
        self.intentions["Tri Burn"].base_amount = 5 if ascension >= 18 else 3
        self._scythe_cooldown = 0

    def on_combat_start(self, floor: int):
        self._scythe_cooldown = 0
        super().on_combat_start(floor)

    def execute_intention(self) -> None:
        from actions.combat import ApplyPowerAction
        from engine.runtime_api import add_action

        will_gain_intangible = not self.has_power("Intangible")
        super().execute_intention()
        if will_gain_intangible:
            add_action(ApplyPowerAction(IntangiblePower(duration=1, owner=self), self, source=self))

    def determine_next_intention(self, floor: int):
        self._scythe_cooldown -= 1
        rng = cast(StreamRandom, get_rng("ai"))
        roll = rng.randint(0, 99)
        history = self.history_intentions
        if not history:
            return self.intentions["Tri Attack" if roll < 50 else "Tri Burn"]

        last = history[-1]
        can_tri_attack = history[-2:] != ["Tri Attack", "Tri Attack"]
        can_scythe = self._scythe_cooldown <= 0
        if roll < 30:
            if last != "Scythe" and can_scythe:
                move = "Scythe"
            elif rng.random_boolean():
                move = "Tri Attack" if can_tri_attack else "Tri Burn"
            else:
                move = "Tri Attack" if last == "Tri Burn" else "Tri Burn"
        elif roll < 65:
            if can_tri_attack:
                move = "Tri Attack"
            else:
                move = "Scythe" if rng.random_boolean() and can_scythe else "Tri Burn"
        elif last != "Tri Burn":
            move = "Tri Burn"
        else:
            move = "Scythe" if rng.random_boolean() and can_scythe else "Tri Attack"

        if move == "Scythe":
            self._scythe_cooldown = 2
        return self.intentions[move]
