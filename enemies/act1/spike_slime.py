"""Spike Slime enemies and their move selection."""
from enemies.act1.spike_slime_intentions import LickIntention, SplitIntention, TackleIntention
from enemies.base import Enemy
from engine.random_streams import get_rng


def _spike_slime_move(history: list[str]) -> str:
    from engine.game_state import game_state

    roll = get_rng("ai").randint(0, 99)
    if roll < 30:
        return "lick" if history[-2:] == ["tackle", "tackle"] else "tackle"
    lick_limit = 1 if game_state.ascension >= 17 else 2
    return "tackle" if history[-lick_limit:] == ["lick"] * lick_limit else "lick"


class SpikeSlimeL(Enemy):
    """Large variant that splits at half HP."""

    select_intention_after_enemy_turn = True

    def __init__(self, max_hp: int | None = None):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range=(67, 73) if ascension >= 7 else (64, 70), max_hp=max_hp)
        self.add_intention(LickIntention(self, frail_amount=3 if ascension >= 17 else 2))
        self.add_intention(TackleIntention(self, damage=18 if ascension >= 2 else 16, slimed_count=2))
        self.add_intention(SplitIntention(self))
        self._split_triggered = False

    def determine_next_intention(self, floor: int = 1):
        if self.history_intentions[-1:] != ["split"] and (
            self._split_triggered or self.hp <= self.max_hp / 2
        ):
            return self.intentions["split"]
        return self.intentions[_spike_slime_move(self.history_intentions)]

    def on_any_hp_lost(self, amount: int, source=None, card=None) -> None:
        if 0 < self.hp <= self.max_hp / 2 and not self._split_triggered:
            self._split_triggered = True
            self.current_intention = self.intentions["split"]


class SpikeSlimeM(Enemy):
    select_intention_after_enemy_turn = True

    def __init__(self, max_hp: int | None = None):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range=(29, 34) if ascension >= 7 else (28, 32), max_hp=max_hp)
        self.add_intention(LickIntention(self, frail_amount=1))
        self.add_intention(TackleIntention(self, damage=10 if ascension >= 2 else 8, slimed_count=1))

    def determine_next_intention(self, floor: int = 1):
        return self.intentions[_spike_slime_move(self.history_intentions)]


class SpikeSlimeS(Enemy):
    select_intention_after_enemy_turn = True

    def __init__(self):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range=(11, 15) if ascension >= 7 else (10, 14))
        self.add_intention(TackleIntention(self, damage=6 if ascension >= 2 else 5))

    def determine_next_intention(self, floor: int = 1):
        get_rng("ai").randint(0, 99)
        return self.intentions["tackle"]
