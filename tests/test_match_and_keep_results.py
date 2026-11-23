import pytest

from actions.card import AddCardAction
from cards.ironclad.searing_blow import SearingBlow
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from events import match_and_keep as mod
from relics.pools import make_relic
from rooms.event import EventRoom


def test_match_board_is_prepared_at_construction_and_reused_in_the_room(monkeypatch):
    pairs = [(Strike(), Strike()) for _ in range(6)]
    labels = {
        id(card): f"{index}{suffix}"
        for index, pair in enumerate(pairs, start=1)
        for suffix, card in zip(("a", "b"), pair)
    }
    generations = []

    def generate_pairs():
        generations.append(1)
        return pairs

    monkeypatch.setattr(mod, "_generate_card_pairs", generate_pairs)
    monkeypatch.setattr(mod, "_matching_state", {})
    misc = game_state.random_streams["misc"]
    misc.seed(42)

    event = mod.MatchAndKeep()
    assert misc.counter == 1
    assert not mod._matching_state
    event.trigger()

    board = mod._matching_state["deck"]
    assert generations == [1]
    assert [labels[id(entry["card"])] for entry in board] == [
        "6a", "4a", "1a", "5b", "2b", "3b", "3a", "1b", "6b", "4b", "2a", "5a",
    ]
    assert misc.counter == 1
    assert misc.random_long() == -1850319953427250933


def test_match_and_keep_end_game_stringifies_card_info_and_returns_actions():
    event = mod.MatchAndKeepAction()
    mod._matching_state = {'matched_cards': [Strike()]}

    result = event._end_game()

    assert result is not None
    assert all(not isinstance(action, AddCardAction) for action in result)
    assert mod._matching_state == {}


def test_match_pair_copies_egg_upgrade_and_obtain_does_not_upgrade_again(monkeypatch):
    searing_blow = SearingBlow()
    game_state.player.relics.append(make_relic("MoltenEgg"))

    def select_searing_blow(*, rarities, **kwargs):
        return searing_blow if rarities == [searing_blow.rarity] else None

    monkeypatch.setattr(mod, "get_random_card", select_searing_blow)

    (first, second), *_ = mod._generate_card_pairs()

    assert isinstance(first, SearingBlow) and isinstance(second, SearingBlow)
    assert first is not second
    assert first.upgrade_level == second.upgrade_level == 1
    assert first.damage == second.damage == 16
    assert first.info().resolve() == second.info().resolve()
    assert second.can_upgrade()

    AddCardAction(second, dest_pile="deck").execute()

    assert any(card is second for card in game_state.player.deck)
    assert second.upgrade_level == 1


@pytest.mark.parametrize("matches", [
    (True, True, True, True, True),
    (False, True, False, True, False),
])
def test_match_event_spends_five_attempts_and_settles_last_pair(monkeypatch, matches):
    monkeypatch.setattr(mod, "_matching_state", {})
    tries_at_menu = []
    initial_size = len(game_state.player.deck)

    def choose(request):
        state = mod._matching_state
        first_index = state["first_selection"]
        available = [index for index, option in enumerate(request.options) if option.enabled]
        attempt = len(tries_at_menu) // 2
        assert attempt < len(matches)
        assert len(game_state.player.deck) - initial_size == sum(matches[:attempt])
        tries_at_menu.append(state["tries_remaining"])
        if first_index is None:
            return [available[0]]
        grid = state["deck"]
        first_id = grid[first_index]["idstr"]
        return [next(index for index in available
                     if (grid[index]["idstr"] == first_id) == matches[attempt])]

    monkeypatch.setattr(game_state, "_resolve_debug_selection", choose)
    room = game_state.current_room = EventRoom()
    event = room.selected_event = mod.MatchAndKeep()
    board_ids = {id(entry["card"]) for entry in event._board}
    room.enter()
    assert game_state.drive_actions() is None
    room._sync_leave_state()

    assert tries_at_menu == [5, 5, 4, 4, 3, 3, 2, 2, 1, 1]
    assert len(game_state.player.deck) - initial_size == sum(matches)
    assert board_ids.isdisjoint(id(card) for card in game_state.player.deck)
    assert not mod._matching_state
    assert room.should_leave
