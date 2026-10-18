"""Owner-specific Ritual timing for players and enemies."""
from typing import Any

from localization import LocalStr
from actions.combat import ApplyPowerAction
from engine.runtime_api import add_action
from powers.base import Power, StackType
from powers.definitions.strength import StrengthPower
from utils.registry import register


@register("power")
class RitualPower(Power):
    name = "Ritual"
    description = "Gain {amount} Strength at the end of your turn."
    stack_type = StackType.INTENSITY
    is_buff = True

    def __init__(self, amount: int = 1, duration: int = -1, owner=None):
        super().__init__(amount=amount, duration=duration, owner=owner)
        self._skip_first_round = True

    def local(self, field: str, **kwargs: Any) -> LocalStr:
        from engine.game_state import game_state

        if field == "description":
            field = "description_enemy" if self.owner is not None and self.owner is not game_state.player else field
            kwargs.setdefault("amount", self.amount)
        return super().local(field, **kwargs)

    def _gain_strength(self):
        if self.owner is not None:
            add_action(ApplyPowerAction(
                StrengthPower(amount=self.amount, owner=self.owner), self.owner,
            ))

    def on_turn_end(self):
        from engine.game_state import game_state

        super().on_turn_end()
        if self.owner is game_state.player:
            self._gain_strength()

    def on_round_end(self):
        from engine.game_state import game_state

        if self.owner is None or self.owner is game_state.player:
            return
        if self._skip_first_round:
            self._skip_first_round = False
            return
        self._gain_strength()
