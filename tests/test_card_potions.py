"""Card potions offer one card chosen from three candidates."""

from typing import cast
import pytest

from actions.base import Action
from actions.card_choice import ChooseAddRandomCardAction
from actions.display import InputRequestAction
from cards.ironclad.bash import Bash
from engine.combat import Combat
from engine.game_state import game_state
from potions.base import Potion
from potions.global_potions import AttackPotion, ColorlessPotion, PowerPotion, SkillPotion
from relics.global_relics.boss import SacredBark
from tests.test_combat_utils import create_test_helper
from utils.types import CardType


def _card_choices(actions: list[Action]) -> list[ChooseAddRandomCardAction]:
    return [
        cast(ChooseAddRandomCardAction, action)
        for action in actions
        if isinstance(action, ChooseAddRandomCardAction)
    ]


def test_card_potions_offer_one_of_three_zero_cost_cards():
    helper = create_test_helper()
    helper.create_player()
    helper.start_combat([])

    cases = (
        (AttackPotion(), CardType.ATTACK, None),
        (SkillPotion(), CardType.SKILL, None),
        (PowerPotion(), CardType.POWER, None),
        (ColorlessPotion(), None, "colorless"),
    )
    for potion, card_type, namespace in cases:
        helper.game_state.action_queue.queue.clear()
        potion.on_use([])
        choices = _card_choices(helper.game_state.action_queue.queue)
        assert len(choices) == 1
        choice = choices[0]
        assert choice.total == 3
        assert choice.pile == "hand"
        assert choice.cost_until_end_of_turn == 0
        assert choice.card_type == card_type
        assert choice.namespace == namespace


def test_sacred_bark_doubles_copies_in_one_three_card_choice():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([])
    player.relics.append(SacredBark())

    AttackPotion().on_use([])

    choices = _card_choices(helper.game_state.action_queue.queue)
    assert len(choices) == 1
    assert all(choice.total == 3 and choice.card_type == CardType.ATTACK for choice in choices)
    assert choices[0].copies == 2


POTION_TYPES = [AttackPotion, SkillPotion, PowerPotion, ColorlessPotion]


def _potion_request(potion_type: type[Potion], bark: bool):
    if bark:
        game_state.player.relics.append(SacredBark())
    potion_type().on_use([])
    game_state.action_queue.execute_next()
    queued = game_state.action_queue.queue
    assert len(queued) == 1
    action = queued.pop(0)
    assert isinstance(action, InputRequestAction)
    selection = cast(InputRequestAction, action)
    assert len(selection.options) == 3
    return selection.request


@pytest.mark.parametrize('potion_type', POTION_TYPES)
@pytest.mark.parametrize('bark', [False, True])
@pytest.mark.parametrize('hand_size', [8, 9, 10])
def test_potion_selection_copies_cost_and_hand_overflow(potion_type: type[Potion], bark: bool, hand_size: int):
    player = game_state.player
    manager = player.card_manager
    manager.get_pile('hand').extend(Bash() for _ in range(hand_size))
    request = _potion_request(potion_type, bark)
    assert request.must_select is (potion_type is ColorlessPotion)
    offered = []
    for option in request.options:
        additions = option.actions
        assert len(additions) == (2 if bark else 1)
        from actions.card_lifecycle import AddCardAction
        assert isinstance(additions[0], AddCardAction)
        offered.append(additions[0].card.idstr)
    assert len(set(offered)) == 3
    for action in request.options[0].actions:
        action.execute()
    added = manager.get_pile('hand')[hand_size:] + manager.get_pile('discard_pile')
    assert len(added) == (2 if bark else 1)
    assert len({id(card) for card in added}) == len(added)
    assert {card.idstr for card in added} == {offered[0]}
    assert all(card.cost_until_end_of_turn == 0 and card.cost == 0 for card in added)
    expected_hand = min(10, hand_size + len(added))
    assert len(manager.get_pile('hand')) == expected_hand
    assert len(manager.get_pile('discard_pile')) == hand_size + len(added) - expected_hand
    if bark:
        added[0].cost_until_end_of_turn = 1
        assert added[1].cost_until_end_of_turn == 0
    Combat([])._start_player_turn()
    assert all(card.cost_until_end_of_turn is None for card in added)


@pytest.mark.parametrize('potion_type', POTION_TYPES)
def test_potion_skip_policy_is_enforced(potion_type: type[Potion], monkeypatch):
    request = _potion_request(potion_type, True)
    game_state.config.mode = 'human'
    game_state.config.auto_select = False
    inputs = iter(['0', '1'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    submission = game_state.resolve_input_request(request)
    if potion_type is ColorlessPotion:
        assert len(submission.actions) == 2
    else:
        assert submission.actions == []
        assert game_state.player.card_manager.get_pile('hand') == []
        assert game_state.player.card_manager.get_pile('discard_pile') == []


def test_generic_random_card_choice_keeps_optional_single_copy_defaults():
    choice = ChooseAddRandomCardAction(namespace='colorless')
    choice.execute()
    action = game_state.action_queue.queue[0]
    assert isinstance(action, InputRequestAction)
    selection = cast(InputRequestAction, action)
    assert not selection.must_select
    assert all(len(option.actions) == 1 for option in selection.options)
