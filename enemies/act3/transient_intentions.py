"""Transient's next attack grows only after an attack has been executed."""
from actions.combat import AttackAction
from engine.runtime_api import add_actions
from enemies.intention import Intention


class TransientAttack(Intention):
    def __init__(self, enemy):
        super().__init__("Attack", enemy)
        from engine.game_state import game_state

        self.base_damage = 40 if game_state.ascension >= 2 else 30

    def get_base_damage(self) -> int:
        return self.base_damage + 10 * self.enemy._attacks_executed

    def execute(self) -> None:
        from engine.game_state import game_state

        damage = self.get_base_damage()
        add_actions([AttackAction(damage, game_state.player, self.enemy, "attack")])
        self.enemy._attacks_executed += 1
