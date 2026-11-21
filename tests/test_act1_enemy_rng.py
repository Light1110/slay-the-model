"""Prepared action-selection traces for the first four migrated enemies."""
import gzip
import json
from pathlib import Path

import pytest

from enemies.act1.acid_slime import AcidSlimeL, AcidSlimeM, AcidSlimeS
from enemies.act1.jaw_worm import JawWorm
from engine.combat import Combat
from engine.game_state import game_state
from engine.random_streams import StreamRandom
from player.player_factory import create_player

REFERENCE = json.loads(gzip.decompress(
    (Path(__file__).with_name("fixtures") / "act1_enemy_ai_reference.json.gz").read_bytes()
))
ENEMIES = {
    "JawWorm": (JawWorm, {1: "chomp", 2: "bellow", 3: "thrash"}),
    "AcidSlime_L": (AcidSlimeL, {1: "corrosive_spit", 2: "tackle", 4: "lick"}),
    "AcidSlime_M": (AcidSlimeM, {1: "corrosive_spit", 2: "tackle", 4: "lick"}),
    "AcidSlime_S": (AcidSlimeS, {1: "tackle", 2: "lick"}),
}


@pytest.mark.parametrize("row", REFERENCE)
def test_migrated_enemy_selection_matches_prepared_reference(row, monkeypatch):
    game_state.ascension = row["ascension"]
    factory, moves = ENEMIES[row["enemy"]]
    enemy = factory()
    enemy.history_intentions[:] = [moves[move] for move in row["history"]]
    rng = StreamRandom(row["seed"])
    monkeypatch.setitem(game_state.random_streams.streams, "ai", rng)
    calls = []
    original_integer, original_boolean = rng.random_int, rng.random_boolean

    def integer(start, end=None):
        result = original_integer(start, end)
        assert (start, end) == (0, 99)
        calls.append(["int", 99, result])
        return result

    def boolean(chance=None):
        result = original_boolean(chance)
        if chance is None:
            calls.append(["bool", result])
        else:
            calls.append(["boolean", chance, result])
        return result

    monkeypatch.setattr(rng, "random_int", integer)
    monkeypatch.setattr(rng, "random_boolean", boolean)

    intent = enemy.determine_next_intention()
    assert intent.name == moves[row["move"]]
    assert calls == row["calls"]
    assert rng.export_state() == row["state"]

    if "next" in row:
        enemy.current_intention = intent
        for next_move in row["next"]:
            enemy.history_intentions.append(enemy.current_intention.name)
            enemy.advance_intention_after_turn(game_state.current_floor)
            assert enemy.current_intention.name == moves[next_move]
        assert rng.export_state() == row["next_state"]


def test_enemy_phase_advances_existing_intent_once_per_enemy(monkeypatch):
    player = create_player("ironclad")
    game_state.player = player
    game_state.ascension = 17
    worm, slime = JawWorm(), AcidSlimeS()
    rng = StreamRandom(0)
    monkeypatch.setitem(game_state.random_streams.streams, "ai", rng)
    combat = Combat(enemies=[worm, slime])
    combat._init_combat()
    assert rng.counter == 2
    assert [e.current_intention.name for e in (worm, slime)] == ["chomp", "lick"]
    game_state.action_queue.clear()

    assert combat.execute_enemy_phase() is None
    assert worm.history_intentions == ["chomp"]
    assert slime.history_intentions == ["lick"]
    assert slime.current_intention.name == "tackle"
    assert rng.counter == 3

    intents = (worm.current_intention, slime.current_intention)
    worm.on_player_turn_start()
    slime.on_player_turn_start()
    assert (worm.current_intention, slime.current_intention) == intents
    assert rng.counter == 3
