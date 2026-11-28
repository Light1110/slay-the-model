from unittest.mock import patch

import pytest

from cards.colorless.necronomicurse import Necronomicurse
from cards.colorless.regret import Regret
from cards.ironclad.defend import Defend
from cards.ironclad.searing_blow import SearingBlow
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from engine.random_streams import StreamRandom
from events.designer_in_spire import DesignerInSpire
from events.the_joust import TheJoust
from rooms.event import EventRoom


def open_event(event):
    room = EventRoom()
    game_state.current_room = room
    room.selected_event = event
    room.enter()
    return room


def next_menu():
    while game_state.pending_input_request is None:
        game_state.action_queue.execute_next()
        assert game_state.pending_input_request is not None or not game_state.action_queue.is_empty()
    return game_state.pending_input_request


def choose(*indices):
    menu = next_menu()
    with patch.object(game_state, "_resolve_debug_selection", return_value=list(indices)):
        submission = game_state.resolve_input_request(menu)
    game_state.pending_input_request = None
    game_state.add_actions(submission.actions, to_front=True)
    return submission.actions


@pytest.mark.parametrize("for_owner", [False, True])
@pytest.mark.parametrize("seed", [0, 4])
def test_joust_rolls_on_start_after_payment_and_settles_once(seed, for_owner):
    rng = game_state.random_streams["misc"]
    rng.seed(seed)
    reference = StreamRandom(seed)
    owner_wins = reference.random_boolean(0.3)
    game_state.player.gold = 50
    room = open_event(TheJoust())

    choose(int(for_owner))
    next_menu()
    assert game_state.player.gold == 0 and rng.counter == 0 and not room.should_leave

    choose(0)
    next_menu()
    assert game_state.player.gold == 0 and rng.export_state() == reference.export_state()
    reveal_actions = choose(0)
    next_menu()
    expected = (250 if for_owner else 100) if for_owner == owner_wins else 0
    assert game_state.player.gold == expected and not room.should_leave
    for action in reveal_actions:
        action.execute()
    assert rng.export_state() == reference.export_state() and game_state.player.gold == expected
    choose(0)
    game_state.drive_actions()
    assert room.should_leave


def test_joust_cannot_charge_or_roll_with_49_gold():
    game_state.player.gold = 49
    rng = game_state.random_streams["misc"]
    before = rng.export_state()
    room = open_event(TheJoust())
    assert [option.enabled for option in next_menu().options] == [False, False, True]
    choose(2)
    game_state.drive_actions()
    assert game_state.player.gold == 49 and rng.export_state() == before and room.should_leave


def designer_for(adjust_one, remove_one):
    for seed in range(32):
        reference = StreamRandom(seed)
        if (reference.random_boolean(), reference.random_boolean()) == (adjust_one, remove_one):
            rng = game_state.random_streams["misc"]
            rng.seed(seed)
            return DesignerInSpire(), rng, reference
    raise AssertionError("missing seed for service combination")


@pytest.mark.parametrize("ascension", [14, 15])
@pytest.mark.parametrize("adjust_one", [False, True])
def test_designer_caches_service_and_upgrades_objects_from_deck(ascension, adjust_one):
    game_state.ascension = ascension
    player = game_state.player
    cost = 50 if ascension == 15 else 40
    player.gold = cost
    deck = [SearingBlow(), SearingBlow(), Defend()]
    player.card_manager.piles["deck"] = deck.copy()
    event, rng, reference = designer_for(adjust_one, True)
    room = open_event(event)
    assert rng.export_state() == reference.export_state()
    choose(0)
    if adjust_one:
        choose(1)
        expected = [deck[1]]
    else:
        expected = deck.copy()
        reference.shuffle(expected)
        expected = expected[:2]
    game_state.drive_actions()
    assert [card.upgrade_level for card in deck] == [int(card in expected) for card in deck]
    assert player.gold == 0 and room.should_leave
    assert rng.export_state() == reference.export_state()


def test_designer_transform_uses_two_selected_cards_and_excludes_protected_cards():
    player = game_state.player
    player.gold = 200
    bottled, protected, first, second = Strike(), Necronomicurse(), Defend(), Regret()
    bottled.bottled = True
    player.card_manager.piles["deck"] = [bottled, first, protected, second]
    event, rng, reference = designer_for(False, False)
    room = open_event(event)
    choose(1)
    menu = next_menu()
    assert len(menu.options) == menu.max_select == 2
    assert rng.export_state() == reference.export_state()
    choose(1, 0)
    game_state.drive_actions()
    assert len(player.deck) == 4 and player.gold == 140
    assert bottled in player.deck and protected in player.deck
    assert first not in player.deck and second not in player.deck
    assert rng.counter == 4 and room.should_leave


@pytest.mark.parametrize("remaining_count", [0, 1, 2])
def test_designer_full_service_removes_before_sampling_remaining_deck(remaining_count):
    player = game_state.player
    player.gold = 90
    removed = SearingBlow()
    remaining = [Defend() for _ in range(remaining_count)]
    player.card_manager.piles["deck"] = [removed, *remaining]
    event, rng, reference = designer_for(True, False)
    room = open_event(event)
    choose(2)
    next_menu()
    assert removed in player.deck and rng.export_state() == reference.export_state()
    choose(0)
    expected = remaining.copy()
    reference.shuffle(expected)
    game_state.drive_actions()
    assert removed not in player.deck and player.gold == 0 and room.should_leave
    assert [card.upgrade_level for card in remaining] == [int(card in expected[:1]) for card in remaining]
    assert rng.export_state() == reference.export_state()


def test_designer_disables_services_without_real_candidates():
    player = game_state.player
    player.gold = 200
    upgraded = Defend()
    upgraded.upgrade()
    player.card_manager.piles["deck"] = [upgraded, Necronomicurse()]
    event, rng, reference = designer_for(True, False)
    room = open_event(event)
    assert [option.enabled for option in next_menu().options] == [False, False, True, True]
    choose(3)
    game_state.drive_actions()
    assert player.gold == 200 and rng.export_state() == reference.export_state() and room.should_leave
