"""Original chest construction and conditional opening RNG traces."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

import actions.misc as misc_actions
from actions.display import InputRequestAction
from actions.reward import AddGoldAction, AddRelicByNameAction
from engine.game_state import game_state
from engine.random_streams import StreamRandom, get_rng
from rooms.treasure import TreasureRoom
from utils.compatible_random import float32
from utils.types import RarityType

REFERENCE = json.loads(gzip.decompress(
    (Path(__file__).with_name("fixtures") / "chest_reward_reference.json.gz").read_bytes()
))


@pytest.mark.parametrize("row", REFERENCE["grid"])
def test_original_shared_reward_draw_for_every_roll(row, monkeypatch):
    expected = row["entry_calls"]
    values = iter(call[3] for call in expected)
    calls = []

    def randint(lo, hi):
        value = next(values)
        calls.append(["int_range", lo, hi, value])
        return value

    monkeypatch.setattr(get_rng("treasure"), "randint", randint)
    room = TreasureRoom()
    room.init()
    assert room.chest_type == row["size"]
    assert room.chest_reward == (row["base_gold"], RarityType[row["tier"]])
    assert calls == expected


@pytest.mark.parametrize("row", REFERENCE["seeded"])
def test_seeded_chest_init_menu_and_open_match_original(row, monkeypatch):
    rng = cast(StreamRandom, get_rng("treasure"))
    rng.seed(int(row["seed"]))
    randint, random_float = rng.randint, rng.random_float
    calls = []

    def trace_int(lo, hi):
        value = randint(lo, hi)
        calls.append(["int_range", lo, hi, value])
        return value

    def trace_float(lo, hi):
        value = random_float(lo, hi)
        calls.append(["float_range", lo, hi, value])
        return value

    def check_state(expected):
        state = rng.export_state()
        assert {key: state[key] for key in expected} == expected

    monkeypatch.setattr(rng, "randint", trace_int)
    monkeypatch.setattr(rng, "random_float", trace_float)
    requested_tiers = []
    get_relic = misc_actions.get_random_relic

    def trace_relic(*, rarities):
        requested_tiers.extend(rarity.name for rarity in rarities)
        return get_relic(rarities=rarities)

    monkeypatch.setattr(misc_actions, "get_random_relic", trace_relic)
    room = TreasureRoom()
    game_state.current_room = room
    room.init()
    assert room.chest_type == row["size"]
    assert room.chest_reward == (row["base_gold"], RarityType[row["tier"]])
    check_state(row["entry_state"])
    room.init()
    room.enter()
    menu = cast(InputRequestAction, game_state.action_queue.queue[-1])
    game_state.action_queue.clear()
    room._build_treasure_menu()
    assert calls == row["entry_calls"]
    check_state(row["entry_state"])
    assert requested_tiers == []

    if row["open"]:
        opener = menu.options[0].actions[0]
        opener.execute()
        queued = list(game_state.action_queue.queue)
        amounts = [cast(AddGoldAction, action).amount
                   for action in queued if isinstance(action, AddGoldAction)]
        assert amounts == ([] if row["gold"] is None else [row["gold"]])
        assert requested_tiers == [row["opened_tier"]]
        assert sum(isinstance(action, AddRelicByNameAction) for action in queued) == 1
        opener.execute()
        assert list(game_state.action_queue.queue) == queued

    expected = [call if call[0] == "int_range" else [call[0], *map(float32, call[1:])]
                for call in row["calls"]]
    assert calls == expected
    check_state(row["final_state"])


def test_older_preselected_room_initializes_reward_once(monkeypatch):
    room = TreasureRoom()
    room.chest_type = "medium"
    del room.chest_reward
    rolls = iter([34])
    monkeypatch.setattr(get_rng("treasure"), "randint", lambda _lo, _hi: next(rolls))
    room.init()
    room.init()
    assert room.chest_reward == (50, RarityType.COMMON)


def test_boss_chest_initialization_keeps_treasure_stream():
    rng = cast(StreamRandom, get_rng("treasure"))
    before = rng.export_state()
    room = TreasureRoom(is_boss=True)
    room.init()
    assert room.chest_type == "boss"
    assert room.chest_reward is None
    assert rng.export_state() == before
