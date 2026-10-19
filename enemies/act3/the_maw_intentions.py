"""The Maw enemy intentions for Slay the Model."""
from engine.runtime_api import add_action, add_actions

from typing import List

from actions.combat import AttackAction, ApplyPowerAction
from enemies.intention import Intention
from powers.definitions.weak import WeakPower
from powers.definitions.frail import FrailPower
from powers.definitions.strength import StrengthPower


class TheMawRoar(Intention):
    """The Maw Roar intention - applies 3 Weak and 3 Frail."""

    def __init__(self, enemy):
        super().__init__("Roar", enemy)

    def execute(self) -> None:
        """Execute Roar intention - applies 3 Weak and 3 Frail."""
        from engine.game_state import game_state
        add_actions(
        [
            ApplyPowerAction(WeakPower(amount=3, duration=3, owner=game_state.player), game_state.player, source=self.enemy),
            ApplyPowerAction(FrailPower(amount=3, duration=3, owner=game_state.player), game_state.player, source=self.enemy)
        ]
        )


class TheMawSlam(Intention):
    """The Maw Slam intention - deals 25 damage."""

    def __init__(self, enemy):
        super().__init__("Slam", enemy)
        self.base_damage = 25

    def execute(self) -> None:
        """Execute Slam intention - deals 25 damage."""
        from engine.game_state import game_state
        add_actions(
        [AttackAction(
            self.base_damage,
            game_state.player,
            self.enemy,
            "attack"
        )]
        )


class TheMawNomNom(Intention):
    """Deal 5 damage per hit, using the selected move's frozen hit count."""

    def __init__(self, enemy):
        super().__init__("Nom Nom", enemy)
        self.base_damage = 5
        self._hits = 1

    def execute(self) -> None:
        from engine.game_state import game_state

        add_actions([
            AttackAction(self.get_base_damage(), game_state.player, self.enemy, "attack")
            for _ in range(self._get_hits())
        ])


class TheMawDrool(Intention):
    """The Maw Drool intention - gains 3 Strength."""

    def __init__(self, enemy):
        super().__init__("Drool", enemy)

    def execute(self) -> None:
        """Execute Drool intention - gains 3 Strength."""
        from engine.game_state import game_state
        add_actions(
        [
            ApplyPowerAction(StrengthPower(amount=3, owner=self.enemy), self.enemy)
        ]
        )
