"""Louse enemies with a shared bite and repeat-limit rule."""
from enemies.act1.louse_intentions import (
    GreenLouseSpitWebIntention,
    LouseBiteIntention,
    RedLouseGrowIntention,
)
from enemies.base import Enemy
from engine.random_streams import get_rng


def _louse_intention(enemy: Enemy, special: str):
    from engine.game_state import game_state

    roll = get_rng("ai").randint(0, 99)
    history = enemy.history_intentions
    if roll < 25:
        special_limit = 1 if game_state.ascension >= 17 else 2
        move = "bite" if history[-special_limit:] == [special] * special_limit else special
    else:
        move = special if history[-2:] == ["bite", "bite"] else "bite"
    return enemy.intentions[move]


def _apply_curl_up(enemy: Enemy) -> None:
    from engine.game_state import game_state
    from powers.definitions.curl_up import CurlUpPower

    ascension = game_state.ascension
    if ascension >= 17:
        bounds = (9, 12)
    elif ascension >= 7:
        bounds = (4, 8)
    else:
        bounds = (3, 7)
    enemy.add_power(CurlUpPower(get_rng("monster_hp").randint(*bounds), owner=enemy))


class RedLouse(Enemy):
    """Louse that can gain Strength."""

    select_intention_after_enemy_turn = True

    def __init__(self):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range=(11, 16) if ascension >= 7 else (10, 15))
        self._bite_damage = get_rng("monster_hp").randint(6, 8) if ascension >= 2 else get_rng("monster_hp").randint(5, 7)
        self.add_intention(LouseBiteIntention(self, self._bite_damage))
        self.add_intention(RedLouseGrowIntention(self))

    def on_combat_start(self, floor: int = 1) -> None:
        super().on_combat_start(floor)
        _apply_curl_up(self)

    def determine_next_intention(self, floor: int = 1):
        return _louse_intention(self, "grow")


class GreenLouse(Enemy):
    """Louse that can apply Weak."""

    select_intention_after_enemy_turn = True

    def __init__(self):
        from engine.game_state import game_state

        ascension = game_state.ascension
        super().__init__(hp_range=(12, 18) if ascension >= 7 else (11, 17))
        self._bite_damage = get_rng("monster_hp").randint(6, 8) if ascension >= 2 else get_rng("monster_hp").randint(5, 7)
        self.add_intention(LouseBiteIntention(self, self._bite_damage))
        self.add_intention(GreenLouseSpitWebIntention(self))

    def on_combat_start(self, floor: int = 1) -> None:
        super().on_combat_start(floor)
        _apply_curl_up(self)

    def determine_next_intention(self, floor: int = 1):
        return _louse_intention(self, "spit_web")
