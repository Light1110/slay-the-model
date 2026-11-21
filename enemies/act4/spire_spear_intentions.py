"""Spire Spear intentions."""
from actions.card import AddCardAction
from actions.combat import ApplyPowerAction, AttackAction
from cards.colorless.burn import Burn
from enemies.intention import Intention
from engine.runtime_api import add_actions
from powers.definitions.strength import StrengthPower
from utils.types import PilePosType


class BurnStrike(Intention):
    """Attack twice and add two Burns."""

    def __init__(self, enemy):
        super().__init__("Burn Strike", enemy)
        self.base_damage = 6 if enemy.ascension >= 3 else 5
        self.hits = 2
        self._burn_pile = "draw_pile" if enemy.ascension >= 18 else "discard_pile"

    def execute(self) -> None:
        from engine.game_state import game_state

        add_actions([
            *(AttackAction(self.base_damage, game_state.player, self.enemy, "attack")
              for _ in range(self.hits)),
            *(AddCardAction(Burn(), self._burn_pile, position=PilePosType.TOP) for _ in range(2)),
        ])


class Skewer(Intention):
    """Attack three times, or four at A3 and above."""

    def __init__(self, enemy):
        super().__init__("Skewer", enemy)
        self.base_damage = 10
        self.hits = 4 if enemy.ascension >= 3 else 3

    def execute(self) -> None:
        from engine.game_state import game_state

        add_actions([
            AttackAction(self.base_damage, game_state.player, self.enemy, "attack")
            for _ in range(self.hits)
        ])


class Piercer(Intention):
    """Grant every living enemy 2 Strength."""

    def __init__(self, enemy):
        super().__init__("Piercer", enemy)
        self.base_strength_gain = 2

    def execute(self) -> None:
        from engine.game_state import game_state

        combat = game_state.current_combat
        enemies = combat.enemies if combat is not None else [self.enemy]
        add_actions([
            ApplyPowerAction(StrengthPower(amount=self.base_strength_gain, owner=enemy), enemy, source=self.enemy)
            for enemy in enemies if enemy.is_alive
        ])
