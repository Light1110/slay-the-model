"""Card-type checks for the divine fountain, wing statue, and falling."""

from typing import cast

from actions.card import RemoveCardAction, RemoveRandomCardAction
from actions.card_choice import ChooseRemoveCardAction
from actions.combat import LoseHPAction
from actions.display import InputRequestAction
from cards.colorless.doubt import Doubt
from cards.ironclad.bash import Bash
from cards.ironclad.defend import Defend
from cards.ironclad.inflame import Inflame
from cards.ironclad.strike import Strike
from engine.game_state import game_state
from events.divine_fountain import DivineFountain
from events.falling import Falling
from events.wing_statue import WingStatue
from tests.test_combat_utils import create_test_helper
from utils.types import CardType


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


def test_divine_fountain_appears_for_curses_and_offers_to_remove_them():
    helper = create_test_helper()
    player = helper.create_player()
    curse = Doubt()
    player.deck.append(curse)

    assert DivineFountain.can_appear()

    drink = _options(DivineFountain())[0]
    removed = [
        action.card
        for action in drink.actions
        if isinstance(action, RemoveCardAction)
    ]
    assert removed == [curse]

    player.deck.clear()
    assert not DivineFountain.can_appear()


def test_wing_statue_offers_gold_for_an_attack_dealing_at_least_10():
    helper = create_test_helper()
    player = helper.create_player()
    bash = Bash()
    player.deck.append(bash)

    weak_options = _options(WingStatue())
    assert not weak_options[1].enabled
    pray = next(
        option
        for option in weak_options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    assert any(isinstance(action, LoseHPAction) and action.amount == 7 for action in pray.actions)
    assert any(isinstance(action, ChooseRemoveCardAction) for action in pray.actions)

    bash.upgrade()
    assert _options(WingStatue())[1].enabled


def test_random_removal_helper_removes_only_the_requested_type():
    helper = create_test_helper()
    player = helper.create_player()
    strike = Strike()
    defend = Defend()
    player.deck.extend([strike, defend])

    RemoveRandomCardAction(card_type=CardType.SKILL).execute()

    assert defend not in player.deck
    assert strike in player.deck


def test_falling_disables_types_missing_from_the_deck():
    player = create_test_helper().create_player()
    player.deck = [Strike()]
    assert [option.enabled for option in _options(Falling())] == [False, False, True]

    player.deck.extend([Defend(), Inflame()])
    assert [option.enabled for option in _options(Falling())] == [True, True, True]
