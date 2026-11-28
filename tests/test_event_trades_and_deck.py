"""Trades and deck changes for We Meet Again, the note, and Match and Keep."""
from engine.random_streams import StreamRandom, get_rng

from typing import cast

import pytest

from actions.card import AddCardAction, RemoveCardAction
from actions.display import InputRequestAction
from cards.colorless.doubt import Doubt
from cards.ironclad.inflame import Inflame
from cards.ironclad.iron_wave import IronWave
from cards.ironclad.strike import Strike
from engine.card_pools import current_pools, original_id, original_rarity
from engine.game_state import game_state
from events.a_note_for_yourself import ANoteForYourself, StoreCardForFutureAction
from events.match_and_keep import _generate_card_pairs
from events.we_meet_again import WeMeetAgain
from potions.ironclad import BloodPotion
from tests.test_combat_utils import create_test_helper
from tests.test_designer_joust_protocol import choose, next_menu, open_event
from utils.types import RarityType


def _requests_in(actions) -> list[InputRequestAction]:
    found = [action for action in actions if isinstance(action, InputRequestAction)]
    return [cast(InputRequestAction, action) for action in found]


def _options(event) -> list:
    game_state.action_queue.clear()
    event.trigger()
    request = next(
        action
        for action in game_state.action_queue.queue
        if isinstance(action, InputRequestAction)
    )
    return list(cast(InputRequestAction, request).options)


def test_we_meet_again_locks_only_the_designated_potion_until_leaving():
    from actions.combat import UsePotionAction

    player = game_state.player
    player.gold = 49
    player.deck.clear()
    potions = [BloodPotion(), BloodPotion()]
    player.potions.extend(potions)
    game_state.random_streams["misc"].seed(0)
    event = WeMeetAgain()
    room = open_event(event)
    assert [option.enabled for option in next_menu().options] == [True, False, False, True]
    offered = event.potion_option
    assert offered is not None and offered.event_locked and not offered.can_use([])
    assert all(not potion.event_locked for potion in potions if potion is not offered)

    UsePotionAction(potion=offered, target=player).execute()
    assert list(player.potions) == potions
    choose(3)
    game_state.drive_actions()
    assert room.should_leave
    room.leave()
    assert offered.can_use([]) and list(player.potions) == potions


@pytest.mark.parametrize("payment", [0, 1, 2])
def test_we_meet_again_preselects_all_three_and_only_collects_the_chosen_payment(payment):
    player = game_state.player
    player.gold = 151
    first, second = Inflame(), Inflame()
    first.bottled = True
    deck = [Strike(), first, Doubt(), second]
    player.card_manager.piles["deck"] = deck.copy()
    potions = [BloodPotion(), BloodPotion()]
    player.potions.extend(potions)
    player.relics.clear()
    game_state.relic_pools.remaining.update(COMMON=["Anchor"], UNCOMMON=["HornCleat"], RARE=["IncenseBurner"])
    rng = game_state.random_streams["misc"]
    rng.seed(0)
    reference = StreamRandom(0)
    potion_order = potions.copy()
    reference.shuffle(potion_order)
    expected_gold = reference.randint(50, 150)
    card_order = [first, second]
    reference.shuffle(card_order)
    event = WeMeetAgain()
    room = open_event(event)
    assert event.potion_option is potion_order[0]
    assert event.gold_amount == expected_gold
    assert event.card_option is card_order[0]
    assert all(option.enabled for option in next_menu().options)
    assert rng.export_state() == reference.export_state()

    choose(payment)
    game_state.drive_actions()
    assert room.should_leave and len(player.relics) == 1
    assert list(player.potions) == [p for p in potions if not (payment == 0 and p is potion_order[0])]
    assert player.deck == [card for card in deck if not (payment == 2 and card is card_order[0])]
    assert player.gold == 151 - (expected_gold if payment == 1 else 0)
    assert rng.export_state() == reference.export_state()
    room.leave()
    assert all(not p.event_locked for p in player.potions)


def test_we_meet_again_disables_missing_requirements_and_can_offer_bottled_card():
    player = game_state.player
    player.gold = 49
    bottled = Inflame()
    bottled.bottled = True
    player.card_manager.piles["deck"] = [Strike(), Doubt(), bottled]
    event = WeMeetAgain()
    open_event(event)

    assert event.card_option is bottled
    assert [option.enabled for option in next_menu().options] == [False, False, True, True]


def test_we_meet_again_rechecks_payment_before_giving_a_relic():
    player = game_state.player
    player.gold = 50
    event = WeMeetAgain()
    room = open_event(event)
    choose(1)
    player.gold = 49
    relics = list(player.relics)
    rng = game_state.random_streams["misc"]
    state = rng.export_state()

    assert not next_menu().options[1].enabled
    assert player.gold == 49 and player.relics == relics and not room.should_leave
    assert rng.export_state() == state
    choose(3)
    game_state.drive_actions()
    assert room.should_leave


def test_note_defaults_to_iron_wave_and_stores_the_card_you_leave(monkeypatch, tmp_path):
    helper = create_test_helper()
    player = helper.create_player()
    strike = Strike()
    doubt = Doubt()
    player.deck.extend([strike, doubt])
    storage = tmp_path / "note.json"
    monkeypatch.setattr("events.a_note_for_yourself.STORAGE_FILE", storage)

    options = _options(ANoteForYourself())
    trades = [option for option in options if option.actions]

    assert len(trades) == 1
    picker = _requests_in(trades[0].actions)[0]
    removed = [
        next(action.card for action in option.actions if isinstance(action, RemoveCardAction))
        for option in picker.options
    ]
    assert removed == [strike]
    added = next(
        action.card
        for action in picker.options[0].actions
        if isinstance(action, AddCardAction)
    )
    assert isinstance(added, IronWave)
    assert added.upgrade_level == 0
    assert added.damage == 5

    for action in picker.options[0].actions:
        action.execute()

    assert strike not in player.deck
    assert any(isinstance(card, IronWave) and card.upgrade_level == 0 for card in player.deck)
    saved = storage.read_text(encoding="utf-8")
    assert '"namespace": "ironclad"' in saved
    assert '"name": "Strike"' in saved
    assert '"upgrade_level": 0' in saved


def test_note_returns_the_stored_card_from_its_namespace(monkeypatch, tmp_path):
    import cards.silent.strike  # noqa: F401

    helper = create_test_helper()
    player = helper.create_player()
    player.deck.append(Strike())
    storage = tmp_path / "note.json"
    storage.write_text(
        '{"stored_card": {"namespace": "ironclad", "name": "Strike", "upgrade_level": 1}}',
        encoding="utf-8",
    )
    monkeypatch.setattr("events.a_note_for_yourself.STORAGE_FILE", storage)

    options = _options(ANoteForYourself())
    picker = _requests_in(next(option.actions for option in options if option.actions))[0]
    added = next(
        action.card
        for action in picker.options[0].actions
        if isinstance(action, AddCardAction)
    )

    assert isinstance(added, Strike)
    assert added.namespace == "ironclad"
    assert added.__class__.__module__ == "cards.ironclad.strike"
    assert added.upgrade_level == 1
    assert added.damage == 9
    assert any(isinstance(action, StoreCardForFutureAction) for action in picker.options[0].actions)


def test_note_hides_the_trade_when_every_card_is_a_curse(monkeypatch, tmp_path):
    helper = create_test_helper()
    player = helper.create_player()
    player.deck.append(Doubt())
    monkeypatch.setattr("events.a_note_for_yourself.STORAGE_FILE", tmp_path / "note.json")

    options = _options(ANoteForYourself())

    assert options
    assert all(not option.actions for option in options)
    assert not (tmp_path / "note.json").exists()


def test_note_stays_hidden_on_ascension_15():
    helper = create_test_helper()
    helper.create_player()
    game_state.config.highest_unlocked_ascension = {game_state.player.namespace.lower(): 15}
    game_state.ascension = 14
    assert ANoteForYourself.can_appear()
    game_state.ascension = 15
    assert not ANoteForYourself.can_appear()


@pytest.mark.parametrize("namespace,starter", [
    ("ironclad", "Bash"), ("silent", "Neutralize"), ("defect", "Zap"), ("watcher", "Eruption"),
])
@pytest.mark.parametrize("ascension", [14, 15])
def test_match_and_keep_uses_ordered_role_slots_and_independent_eligible_curses(namespace, starter, ascension):
    helper = create_test_helper()
    player = helper.create_player()
    player.namespace = namespace
    game_state.ascension = ascension
    game_state.random_streams["card"].seed(9)
    game_state.random_streams["shuffle"].seed(9)
    pools = current_pools().current
    last_common = pools[(namespace, "COMMON")][-1]
    pools[(namespace, "COMMON")][:] = [last_common]
    colorless_before = pools[("colorless", None)].copy()
    pairs = _generate_card_pairs()
    originals = [card for card, _ in pairs]

    assert len(originals) == 6
    assert len({id(card) for pair in pairs for card in pair}) == 12
    assert all(original_id(first) == original_id(second) for first, second in pairs)
    assert [card.namespace for card in originals[:3]] == [namespace] * 3
    assert [original_rarity(card) for card in originals[:3]] == [
        RarityType.RARE, RarityType.UNCOMMON, RarityType.COMMON,
    ]
    assert original_id(originals[2]) == last_common
    assert original_id(originals[-1]) == starter
    if ascension >= 15:
        assert [original_id(card) for card in originals[3:5]] == ["Normality", "Normality"]
        assert pools[("colorless", None)] == colorless_before
        assert game_state.random_streams["card"].counter == 5
        assert game_state.random_streams["shuffle"].counter == 0
    else:
        assert originals[3].namespace == "colorless"
        assert original_rarity(originals[3]) == RarityType.UNCOMMON
        assert original_rarity(originals[4]) == RarityType.CURSE
        assert pools[("colorless", None)] != colorless_before
        assert game_state.random_streams["card"].counter == 4
        assert game_state.random_streams["shuffle"].counter == 1
