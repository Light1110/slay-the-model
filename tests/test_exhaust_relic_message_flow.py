from actions.card import ExhaustCardAction
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from relics.character.ironclad import CharonsAshes
from relics.global_relics.rare import DeadBranch
from tests.test_combat_utils import create_test_helper
from utils.result_types import MultipleActionsResult, SingleActionResult


def _execute_result(result):
    if result is None:
        return

    if isinstance(result, SingleActionResult):
        _execute_result(result.action.execute())
        return

    if isinstance(result, MultipleActionsResult):
        for action in result.actions:
            _execute_result(action.execute())
        return

    if hasattr(result, "execute"):
        _execute_result(result.execute())


def test_exhaust_card_action_publishes_message_for_charons_ashes():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=12)
    helper.start_combat([enemy])

    exhaust_target = Strike()
    helper.add_card_to_hand(exhaust_target)
    player.relics.append(CharonsAshes())

    result = ExhaustCardAction(card=exhaust_target, source_pile="hand").execute()
    _execute_result(result)

    assert exhaust_target in player.card_manager.piles["exhaust_pile"]
    assert enemy.hp == 9


def test_exhaust_card_action_publishes_message_for_dead_branch():
    helper = create_test_helper()
    player = helper.create_player(hp=80, max_hp=80, energy=3)
    enemy = helper.create_enemy(Cultist, hp=12)
    helper.start_combat([enemy])

    exhaust_target = Strike()
    helper.add_card_to_hand(exhaust_target)
    player.relics.append(DeadBranch())

    initial_hand_size = len(player.card_manager.piles["hand"])

    result = ExhaustCardAction(card=exhaust_target, source_pile="hand").execute()
    _execute_result(result)

    assert exhaust_target in player.card_manager.piles["exhaust_pile"]
    assert len(player.card_manager.piles["hand"]) == initial_hand_size
