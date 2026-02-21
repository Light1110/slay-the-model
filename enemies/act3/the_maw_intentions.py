"""The Maw enemy intentions for Slay the Model."""

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

    def execute(self) -> List:
        """Execute Roar intention - applies 3 Weak and 3 Frail."""
        from engine.game_state import game_state
        return [
            ApplyPowerAction(WeakPower(stacks=3, owner=game_state.player), game_state.player),
            ApplyPowerAction(FrailPower(stacks=3, owner=game_state.player), game_state.player)
        ]


class TheMawSlam(Intention):
    """The Maw Slam intention - deals 25 damage."""

    def __init__(self, enemy):
        super().__init__("Slam", enemy)
        self.base_damage = 25

    def execute(self) -> List:
        """Execute Slam intention - deals 25 damage."""
        from engine.game_state import game_state
        return [AttackAction(
            self.enemy.get_damage(self.base_damage),
            game_state.player,
            self.enemy,
            "slam"
        )]


class TheMawNomNom(Intention):
    """The Maw Nom Nom intention - deals 5*N damage where N = turn/2 rounded up."""

    def __init__(self, enemy):
        super().__init__("Nom Nom", enemy)

    def execute(self) -> List:
        """Execute Nom Nom intention - deals 5*N damage where N = turn/2 rounded up."""
        from engine.game_state import game_state
        current_turn = getattr(self.enemy, '_turn_count', 1)
        n = (current_turn + 1) // 2  # Round up: (turn + 1) // 2
        damage = 5 * n
        return [AttackAction(
            self.enemy.get_damage(damage),
            game_state.player,
            self.enemy,
            "nom_nom"
        )]


class TheMawDrool(Intention):
    """The Maw Drool intention - gains 3 Strength."""

    def __init__(self, enemy):
        super().__init__("Drool", enemy)

    def execute(self) -> List:
        """Execute Drool intention - gains 3 Strength."""
        return [
            ApplyPowerAction(StrengthPower(stacks=3, owner=self.enemy), self.enemy)
        ]