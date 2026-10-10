"""Card-type checks for the divine fountain, wing statue, and falling."""

from typing import cast

from actions.card import RemoveCardAction, RemoveRandomCardAction
from actions.card_choice import ChooseRemoveCardAction
from actions.combat import LoseHPAction
from actions.display import InputRequestAction
from actions.reward import AddGoldAction
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


def _option_for(options, card_type: CardType):
    return next(
        option
        for option in options
        if any(
            isinstance(action, RemoveRandomCardAction) and action.card_type == card_type
            for action in option.actions
        )
    )


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
    assert not any(
        isinstance(action, AddGoldAction)
        for option in weak_options
        for action in option.actions
    )
    pray = next(
        option
        for option in weak_options
        if any(isinstance(action, LoseHPAction) for action in option.actions)
    )
    assert any(isinstance(action, LoseHPAction) and action.amount == 7 for action in pray.actions)
    assert any(isinstance(action, ChooseRemoveCardAction) for action in pray.actions)

    bash.upgrade()
    destroy = next(
        option
        for option in _options(WingStatue())
        if any(isinstance(action, AddGoldAction) for action in option.actions)
    )
    gold = next(action for action in destroy.actions if isinstance(action, AddGoldAction))
    assert 50 <= gold.amount <= 80


def test_falling_removes_a_deck_card_and_locks_missing_types():
    helper = create_test_helper()
    player = helper.create_player()
    strike = Strike()
    defend = Defend()
    player.deck.extend([strike, defend])

    RemoveRandomCardAction(card_type=CardType.SKILL).execute()

    assert defend not in player.deck
    assert strike in player.deck

    player.deck.clear()
    player.deck.append(Strike())
    options = _options(Falling())
    assert _option_for(options, CardType.ATTACK).enabled
    assert not _option_for(options, CardType.SKILL).enabled
    assert not _option_for(options, CardType.POWER).enabled

    player.deck.extend([Defend(), Inflame()])
    options = _options(Falling())
    assert _option_for(options, CardType.ATTACK).enabled
    assert _option_for(options, CardType.SKILL).enabled
    assert _option_for(options, CardType.POWER).enabled
