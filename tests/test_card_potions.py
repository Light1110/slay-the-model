"""Card potions offer one card chosen from three candidates."""

from typing import cast

from actions.base import Action
from actions.card_choice import ChooseAddRandomCardAction
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


def test_sacred_bark_repeats_the_three_card_choice():
    helper = create_test_helper()
    player = helper.create_player()
    helper.start_combat([])
    player.relics.append(SacredBark())

    AttackPotion().on_use([])

    choices = _card_choices(helper.game_state.action_queue.queue)
    assert len(choices) == 2
    assert all(choice.total == 3 and choice.card_type == CardType.ATTACK for choice in choices)
