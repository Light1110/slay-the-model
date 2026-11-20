"""Advanced menu ordering, exclusion rules and stream consumption."""
import gzip
import json
from pathlib import Path
from typing import cast

import pytest

from actions.card import ChooseAddRandomCardAction
from actions.display import InputRequestAction
from engine.game_state import game_state
from engine.random_streams import StreamRandom, current_streams
from localization import ConcatLocalStr, LocalStr
from player.player_factory import create_player
from rooms.neo import NeoRewardRoom

REFERENCE = json.loads(gzip.decompress(
    (Path(__file__).with_name("fixtures") / "neow_menu_protocol_reference.json.gz").read_bytes()
))
KEYS = {
    "THREE_CARDS": "choose_card_option",
    "ONE_RANDOM_RARE_CARD": "random_rare_card_option",
    "REMOVE_CARD": "remove_card_option",
    "UPGRADE_CARD": "upgrade_card_option",
    "TRANSFORM_CARD": "transform_card_option",
    "RANDOM_COLORLESS": "uncommon_colorless_option",
    "THREE_SMALL_POTIONS": "three_random_potions_option",
    "RANDOM_COMMON_RELIC": "random_common_relic_option",
    "TEN_PERCENT_HP_BONUS": "max_hp_option",
    "THREE_ENEMY_KILL": "neow_option",
    "HUNDRED_GOLD": "receive_100_gold_option",
    "TEN_PERCENT_HP_LOSS": "lose_max_hp_option",
    "NO_GOLD": "lose_all_gold_option",
    "CURSE": "obtain_curse_option",
    "PERCENT_DAMAGE": "take_damage_option",
    "RANDOM_COLORLESS_2": "choose_rare_colorless_card_option",
    "REMOVE_TWO": "remove_two_cards_option",
    "ONE_RARE_RELIC": "random_rare_relic_option",
    "THREE_RARE_CARDS": "choose_rare_card_option",
    "TWO_FIFTY_GOLD": "gain_250_gold_option",
    "TRANSFORM_TWO_CARDS": "transform_two_cards_option",
    "TWENTY_PERCENT_HP_BONUS": "big_max_hp_option",
    "BOSS_RELIC": "replace_starter_relic_option",
}


def open_menu(monkeypatch, *, advanced=True):
    game_state.run_history["reached_exordium_boss"] = advanced
    room = NeoRewardRoom()
    # Pause the debug input driver at the room's menu for inspection.
    with monkeypatch.context() as patch:
        patch.setattr(game_state, "drive_actions", lambda: None)
        room.enter()
    return next(cast(InputRequestAction, action) for action in game_state.action_queue.queue
                if isinstance(action, InputRequestAction))


def assert_menu(request, row):
    first, second, mixed, fourth = request.options
    combined = cast(ConcatLocalStr, mixed.name)
    names = [first.name, second.name, combined.right, fourth.name]
    assert [cast(LocalStr, name).key for name in names] == [
        "blessing." + KEYS[kind] for kind in row["types"]
    ]
    assert cast(LocalStr, combined.left).key == "blessing." + KEYS[row["drawback"]]


@pytest.mark.parametrize("row", REFERENCE["grid"])
def test_every_candidate_and_filtered_index_matches_reference(row, monkeypatch):
    calls = []
    values = iter(call[3] for call in row["calls"])

    def draw(self, start, end=None):
        lo, hi = (0, start) if end is None else (start, end)
        value = next(values)
        calls.append(["int_range", lo, hi, value])
        return value

    monkeypatch.setattr(StreamRandom, "random_int", draw)
    assert_menu(open_menu(monkeypatch), row)
    assert calls == row["calls"]


@pytest.mark.parametrize("row", REFERENCE["seeded"])
@pytest.mark.parametrize("role", ["ironclad", "silent", "defect", "watcher"])
@pytest.mark.parametrize("ascension", [0, 20])
def test_seeded_menu_and_first_card_draw_match_reference(row, role, ascension, monkeypatch):
    game_state.player = create_player(role, ascension=ascension)
    streams = current_streams()
    monkeypatch.setattr(streams, "seed", int(row["seed"]))
    before = {name: stream.export_state() for name, stream in streams.streams.items()}
    calls = []
    original = StreamRandom.random_int

    def draw(self, start, end=None):
        value = original(self, start, end)
        if self is streams.neow_rng:
            lo, hi = (0, start) if end is None else (start, end)
            calls.append(["int_range", lo, hi, value])
        return value

    monkeypatch.setattr(StreamRandom, "random_int", draw)
    request = open_menu(monkeypatch)
    assert_menu(request, row)
    assert calls == row["calls"]
    assert {name: stream.export_state() for name, stream in streams.streams.items()} == before
    state = streams.neow_rng.export_state()
    assert {key: state[key] for key in row["state"]} == row["state"]

    if row["types"][0] == "THREE_CARDS":
        action = request.options[0].actions[0]
        assert isinstance(action, ChooseAddRandomCardAction)
        rarity_rolls = []
        fallback = streams.neow_rng.random_boolean

        def rarity(chance=None):
            value = fallback(chance)
            rarity_rolls.append((chance, value))
            return value

        monkeypatch.setattr(streams.neow_rng, "random_boolean", rarity)
        action.execute()
        assert rarity_rolls[0] == (0.33, row["next_card_rarity"])


def test_basic_menu_uses_no_advanced_draws(monkeypatch):
    before = current_streams().neow_rng.export_state()
    request = open_menu(monkeypatch, advanced=False)
    assert [cast(LocalStr, option.name).key for option in request.options] == [
        "blessing.max_hp_option", "blessing.neow_option",
    ]
    assert current_streams().neow_rng.export_state() == before
