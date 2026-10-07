"""Maw Bank pays on a floor climb, and Necronomicon replays a costly attack."""

from actions.combat_cards import PlayCardBHAction
from actions.map_selection import MoveToMapNodeAction
from actions.reward import AddRelicAction
from cards.base import COST_X
from cards.ironclad.bash import Bash
from cards.ironclad.strike import Strike
from cards.silent.skewer import Skewer
from enemies.act1.cultist import Cultist
from engine.messages import PlayerTurnStartedMessage
from map.map_manager import MapManager
from map.map_node import MapNode
from relics.global_relics.common import MawBank
from relics.global_relics.event import Necronomicon
from tests.test_combat_utils import create_test_helper
from utils.types import RoomType


def _prepare_map(helper) -> None:
    manager = MapManager(seed=1, act_id=1)
    manager.map_data.nodes = [
        [MapNode(0, 0, RoomType.NEO, connections_up=[0])],
        [MapNode(1, 0, RoomType.REST)],
    ]
    helper.game_state.map_manager = manager
    helper.game_state.current_act = 1
    helper.game_state.current_floor = 0
    manager.map_data.set_current_position(0, 0)


def _climb(helper) -> None:
    MoveToMapNodeAction(floor=1, position=0).execute()
    helper.game_state.drive_actions()


def _track_plays(card):
    calls = []
    original = card.on_play

    def wrapped(targets=None):
        played_targets = [] if targets is None else list(targets)
        calls.append(played_targets)
        return original(played_targets)

    card.on_play = wrapped
    return calls


def test_maw_bank_pays_for_a_floor_climb_and_not_for_combat_start():
    helper = create_test_helper()
    player = helper.create_player()
    AddRelicAction(MawBank()).execute()
    before = player.gold
    helper.start_combat([helper.create_enemy(Cultist, hp=20)])
    helper.game_state.drive_actions()
    assert player.gold == before

    _prepare_map(helper)
    _climb(helper)
    assert player.gold == before + 12


def test_maw_bank_stops_after_gold_is_spent_in_a_shop():
    helper = create_test_helper()
    player = helper.create_player()
    relic = MawBank()
    AddRelicAction(relic).execute()
    helper.game_state.gold_spent_in_shop = 15
    before = player.gold

    _prepare_map(helper)
    _climb(helper)

    assert player.gold == before
    assert relic.still_working is False


def test_shop_spending_before_obtaining_maw_bank_does_not_disable_it():
    helper = create_test_helper()
    player = helper.create_player()
    helper.game_state.gold_spent_in_shop = 40
    AddRelicAction(MawBank()).execute()
    before = player.gold

    _prepare_map(helper)
    _climb(helper)

    assert player.gold == before + 12


def test_necronomicon_replays_the_first_attack_that_cost_at_least_two():
    helper = create_test_helper()
    player = helper.create_player(energy=5)
    enemy = helper.create_enemy(Cultist, hp=80)
    helper.start_combat([enemy])
    player.relics.append(Necronomicon())

    first = Bash()
    second = Bash()
    first_calls = _track_plays(first)
    second_calls = _track_plays(second)
    helper.add_card_to_hand(first)
    helper.add_card_to_hand(second)

    PlayCardBHAction(first, [enemy]).execute()
    helper.game_state.drive_actions()
    PlayCardBHAction(second, [enemy]).execute()
    helper.game_state.drive_actions()

    assert first_calls == [[enemy], [enemy]]
    assert second_calls == [[enemy]]


def test_necronomicon_ignores_attacks_that_cost_less_than_two():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])
    player.relics.append(Necronomicon())
    strike = Strike()
    calls = _track_plays(strike)
    helper.add_card_to_hand(strike)

    PlayCardBHAction(strike, [enemy]).execute()
    helper.game_state.drive_actions()

    assert calls == [[enemy]]


def test_necronomicon_uses_energy_spent_on_an_x_cost_attack():
    helper = create_test_helper()
    player = helper.create_player(energy=2)
    enemy = helper.create_enemy(Cultist, hp=80)
    helper.start_combat([enemy])
    player.relics.append(Necronomicon())
    skewer = Skewer()
    assert skewer._cost == COST_X
    calls = _track_plays(skewer)
    helper.add_card_to_hand(skewer)

    PlayCardBHAction(skewer, [enemy]).execute()
    helper.game_state.drive_actions()

    assert calls == [[enemy], [enemy]]


def test_necronomicon_resets_at_the_start_of_each_player_turn():
    helper = create_test_helper()
    player = helper.create_player(energy=3)
    enemy = helper.create_enemy(Cultist, hp=40)
    helper.start_combat([enemy])
    relic = Necronomicon()
    relic.double_attack_played = True
    player.relics.append(relic)

    helper.game_state.publish_message(PlayerTurnStartedMessage(owner=player, enemies=[enemy]))

    assert relic.double_attack_played is False
