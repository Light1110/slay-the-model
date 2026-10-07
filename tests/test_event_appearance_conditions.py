"""Appearance rules for winding halls, the nest, forgotten altar, and pleading vagrant."""

from typing import cast

from actions.card import AddCardAction
from actions.combat import ModifyMaxHpAction
from actions.combat_damage import HealAction, LoseHPAction
from actions.display import InputRequestAction
from actions.reward import AddGoldAction, LoseGoldAction, LoseRelicAction
from cards.colorless.decay import Decay
from engine.game_state import game_state
from events.event_pool import event_pool
from events.forgotten_altar import ForgottenAltar
from events.pleading_vagrant import PleadingVagrant
from events.the_nest import TheNest
from events.winding_halls import WindingHalls
from relics.global_relics.event import GoldenIdol
from tests.test_combat_utils import create_test_helper


def _available(act: int) -> set[type]:
    return {metadata.event_class for metadata in event_pool.get_available_events(act)}


def _input_request() -> InputRequestAction:
    request = next(
        action
        for action in game_state.action_queue.queue
        if isinstance(action, InputRequestAction)
    )
    return cast(InputRequestAction, request)


def _options(event) -> list:
    game_state.action_queue.clear()
    event.trigger()
    return list(_input_request().options)


def test_act_events_appear_below_ascension_15_and_without_gold():
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = 0
    game_state.player.gold = 0

    act_2 = _available(2)
    act_3 = _available(3)

    assert TheNest in act_2
    assert ForgottenAltar in act_2
    assert PleadingVagrant in act_2
    assert WindingHalls in act_3


def test_ascension_changes_amounts_without_hiding_the_events():
    helper = create_test_helper()
    helper.create_player()
    game_state.ascension = 15
    game_state.player.gold = 0

    assert TheNest in _available(2)
    assert WindingHalls in _available(3)

    nest_gold = next(
        action
        for option in _options(TheNest())
        for action in option.actions
        if isinstance(action, AddGoldAction)
    )
    assert nest_gold.amount == 50

    halls_actions = [
        action
        for option in _options(WindingHalls())
        for action in option.actions
    ]
    assert any(
        isinstance(action, LoseHPAction) and action.percent == 0.18
        for action in halls_actions
    )
    assert any(
        isinstance(action, HealAction) and action.percent == 0.20
        for action in halls_actions
    )


def test_forgotten_altar_has_no_leave_and_keeps_the_three_offerings():
    helper = create_test_helper()
    player = helper.create_player()
    player.relics.append(GoldenIdol())
    game_state.ascension = 0

    options = _options(ForgottenAltar())

    assert options
    assert all(option.actions for option in options)
    assert any(
        any(isinstance(action, LoseRelicAction) for action in option.actions)
        for option in options
    )
    sacrifice = next(
        option
        for option in options
        if any(isinstance(action, ModifyMaxHpAction) for action in option.actions)
    )
    hp_loss = next(
        action for action in sacrifice.actions if isinstance(action, LoseHPAction)
    )
    assert hp_loss.percent == 0.25
    assert any(
        any(isinstance(action, AddCardAction) and isinstance(action.card, Decay)
            for action in option.actions)
        for option in options
    )

    game_state.ascension = 15
    ascended = _options(ForgottenAltar())
    ascended_loss = next(
        action
        for option in ascended
        for action in option.actions
        if isinstance(action, LoseHPAction)
    )
    assert ascended_loss.percent == 0.35


def test_pleading_vagrant_hides_the_gold_offer_until_the_player_can_pay():
    helper = create_test_helper()
    helper.create_player()
    game_state.player.gold = 0

    broke = _options(PleadingVagrant())
    assert any(not option.enabled for option in broke)
    assert any(option.enabled and option.actions for option in broke)
    assert any(option.enabled and not option.actions for option in broke)

    game_state.player.gold = 85
    paid = _options(PleadingVagrant())
    offer = next(
        option
        for option in paid
        if any(isinstance(action, LoseGoldAction) for action in option.actions)
    )
    assert offer.enabled
