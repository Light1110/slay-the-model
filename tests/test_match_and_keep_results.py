from cards.ironclad.strike import Strike
from engine.game_state import game_state
from events import match_and_keep as mod


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
    assert mod._matching_state == {}
