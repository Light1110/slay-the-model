"""Mind Bloom combat rewards and Knowing Skull independent HP payments."""
from engine.random_streams import get_rng, StreamRandom
from typing import cast

import pytest

from actions.combat import StartFightAction
from actions.display import InputRequestAction
from cards.colorless.finesse import Finesse
from cards.ironclad.bash import Bash
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from enemies.act1.slime_boss import SlimeBoss
from enemies.act1.the_guardian import TheGuardian
from enemies.act1.the_hexaghost import TheHexaghost
from engine.combat import Combat
from engine.game_state import game_state
from events.knowing_skull import KnowingSkull
from events.mind_bloom import MindBloom
from localization import resolve_text, set_language
from potions.global_potions import EnergyPotion
from relics.global_relics.boss import Sozu
from relics.global_relics.rare import BirdFacedUrn
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState
from utils.types import CombatType, RarityType


@pytest.fixture
def player():
    helper = create_test_helper()
    player = helper.create_player(hp=100, max_hp=100)
    game_state.config.auto_select = False
    game_state.action_queue.clear()
    return player


def queued_menu() -> InputRequestAction:
    menu = game_state.action_queue.queue[-1]
    assert isinstance(menu, InputRequestAction)
    game_state.action_queue.clear()
    return cast(InputRequestAction, menu)


@pytest.mark.parametrize('boss_class', [TheGuardian, TheHexaghost, SlimeBoss])
@pytest.mark.parametrize('ascension,gold', [(12, 50), (13, 25), (15, 25)])
def test_bloom_creates_real_boss_only_after_selection(player, monkeypatch, boss_class, ascension, gold):
    game_state.ascension = ascension
    seen = []
    def shuffle(classes):
        seen.append(tuple(classes))
        classes.remove(boss_class)
        classes.insert(0, boss_class)
    monkeypatch.setattr(get_rng("misc"), "shuffle", shuffle)
    event = MindBloom()
    event.trigger()
    menu = queued_menu()
    assert not seen
    assert str(gold) in resolve_text(menu.options[0].detail)
    for action in menu.options[0].actions:
        action.execute()
    fight = cast(StartFightAction, game_state.action_queue.queue[0])
    assert isinstance(fight, StartFightAction)
    assert len(fight.enemies) == 1
    assert type(fight.enemies[0]) is boss_class
    assert seen == [(TheGuardian, TheHexaghost, SlimeBoss)]
    assert fight.combat_type == CombatType.NORMAL
    assert event.event_ended


@pytest.mark.parametrize('ascension,gold', [(12, 50), (13, 25)])
@pytest.mark.parametrize('skip_card', [False, True])
def test_bloom_win_grants_rare_relic_gold_and_optional_deck_reward_once(player, monkeypatch, ascension, gold, skip_card):
    game_state.ascension = ascension
    game_state.current_act = 3
    game_state.current_floor = 38
    player.namespace = 'ironclad'
    rare_pool = ["BirdFacedUrn", "Calipers"]
    game_state.relic_pools.remaining["RARE"] = rare_pool
    offered = [Strike(), Defend(), Bash()]
    monkeypatch.setattr('actions.card_choice.get_card_reward_options', lambda **kwargs: offered)
    requests = []
    def select(request):
        requests.append(request)
        return [] if skip_card else [1]
    monkeypatch.setattr(game_state, '_resolve_debug_selection', select)
    fights = []
    def win(combat):
        fights.append(combat)
        assert rare_pool == ["Calipers"]
        assert not player.relics
        combat._init_combat()
        return GameTerminalState.COMBAT_WIN
    monkeypatch.setattr(Combat, 'start', win)
    MindBloom().trigger()
    menu = queued_menu()
    initial_gold = player.gold
    game_state.action_queue.add_actions(menu.options[0].actions)
    assert game_state.drive_actions() is None
    assert len(fights) == 1
    assert rare_pool == ["Calipers"]
    assert player.gold == initial_gold + gold
    assert len(player.relics) == 1 and isinstance(player.relics[0], BirdFacedUrn)
    assert list(player.deck) == ([] if skip_card else [offered[1]])
    assert not player.card_manager.get_pile('hand')
    assert len(requests) == 1 and not requests[0].must_select
    assert game_state.current_act == 3 and game_state.current_floor == 38
    assert game_state.drive_actions() is None
    assert player.gold == initial_gold + gold and len(player.relics) == 1


@pytest.mark.parametrize('result', [GameTerminalState.GAME_LOSE, GameTerminalState.COMBAT_ESCAPE])
def test_bloom_failure_or_escape_does_not_grant_rewards(player, monkeypatch, result):
    monkeypatch.setattr(Combat, 'start', lambda _: result)
    rare_pool = ["BirdFacedUrn", "Calipers"]
    game_state.relic_pools.remaining["RARE"] = rare_pool
    MindBloom().trigger()
    menu = queued_menu()
    initial_gold = player.gold
    game_state.action_queue.add_actions(menu.options[0].actions)
    outcome = game_state.drive_actions()
    assert outcome == (GameTerminalState.GAME_LOSE if result == GameTerminalState.GAME_LOSE else None)
    assert rare_pool == ["Calipers"]
    assert not player.relics and not player.deck
    assert player.gold == initial_gold


@pytest.mark.parametrize('ascension,max_hp', [(0, 80), (14, 200), (15, 80), (20, 200)])
def test_skull_initial_costs_are_fixed_and_menu_refresh_is_pure(player, ascension, max_hp):
    game_state.ascension = ascension
    player.max_hp = max_hp
    event = KnowingSkull()
    for _ in range(3):
        event.trigger()
        menu = queued_menu()
        for option in menu.options:
            assert '6' in resolve_text(option.detail)
            assert option.actions[0].amount == 6
    assert (event.potion_cost, event.gold_cost, event.card_cost, event.leave_cost) == (6, 6, 6, 6)
    assert not KnowingSkull().event_ended


@pytest.mark.parametrize('sequence,hp_loss,costs,gold_gain,potions,cards', [
    ([0, 1, 0, 3], 25, (8, 7, 6), 90, 2, 0),
    ([2, 2, 3], 19, (6, 6, 8), 0, 0, 2),
    ([1, 1, 3], 19, (6, 8, 6), 180, 0, 0),
])
def test_skull_mixed_choices_pay_and_increment_independently(
    player, monkeypatch, sequence, hp_loss, costs, gold_gain, potions, cards,
):
    choices = iter(sequence)
    seen_costs = []
    def select(request):
        seen_costs.append([option.actions[0].amount for option in request.options])
        return [next(choices)]
    monkeypatch.setattr(game_state, '_resolve_debug_selection', select)
    monkeypatch.setattr('events.knowing_skull.get_random_potion', lambda **kwargs: EnergyPotion())
    card_calls = []
    def draw_card(**kwargs):
        card_calls.append(kwargs)
        return Finesse()
    monkeypatch.setattr('actions.card_transform.get_random_card', draw_card)
    initial_gold = player.gold
    event = KnowingSkull()
    event.trigger()
    assert game_state.drive_actions() is None
    assert player.hp == 100 - hp_loss
    assert (event.potion_cost, event.gold_cost, event.card_cost) == costs
    assert all(cost[3] == 6 for cost in seen_costs)
    assert player.gold == initial_gold + gold_gain
    assert len(player.potions) == potions and len(player.deck) == cards
    assert not player.card_manager.get_pile('hand')
    assert all(call['namespaces'] == ['colorless'] and call['rarities'] == [RarityType.UNCOMMON] for call in card_calls)
    assert event.event_ended and game_state.action_queue.is_empty()
    fresh = KnowingSkull()
    assert (fresh.potion_cost, fresh.gold_cost, fresh.card_cost) == (6, 6, 6)


@pytest.mark.parametrize('choice', [0, 1, 2, 3])
@pytest.mark.parametrize('hp', [1, 6])
def test_skull_lethal_payment_stops_before_reward_or_next_menu(player, monkeypatch, choice, hp):
    player.hp = hp
    potion_rng = game_state.random_streams["potion"]
    before_potion = potion_rng.export_state()
    monkeypatch.setattr(game_state, '_resolve_debug_selection', lambda request: [choice])
    event = KnowingSkull()
    initial_gold = player.gold
    event.trigger()
    assert game_state.drive_actions() == GameTerminalState.GAME_LOSE
    assert player.is_dead() and event.event_ended
    assert player.gold == initial_gold and not player.deck and not player.potions
    assert potion_rng.export_state() == before_potion
    assert (event.potion_cost, event.gold_cost, event.card_cost) == (6, 6, 6)
    assert game_state.pending_input_request is None and game_state.action_queue.is_empty()


def test_skull_auto_selection_uses_paid_exit_and_terminates(player, monkeypatch):
    game_state.config.auto_select = True
    monkeypatch.setattr(game_state, '_resolve_debug_selection', lambda request: [1])
    event = KnowingSkull()
    initial_gold = player.gold
    event.trigger()
    assert game_state.drive_actions() is None
    assert player.hp == 88 and player.gold == initial_gold + 90
    assert event.gold_cost == 7 and event.event_ended
    assert game_state.action_queue.is_empty()


@pytest.mark.parametrize("sozu", [False, True])
@pytest.mark.parametrize("full", [False, True])
def test_skull_potion_payment_draw_and_inventory(player, monkeypatch, sozu, full):
    player.character = "Ironclad"
    if sozu:
        player.relics.append(Sozu())
    originals = [EnergyPotion() for _ in range(player.potion_limit)] if full else []
    player.potions.extend(originals)
    rng = game_state.random_streams["potion"]
    rng.seed(42)
    choices = iter([0, 0, 3])
    menus = []

    def select(request):
        assert request.title != "ui.potion_full_title"
        menus.append((player.hp, request.options[0].detail.kwargs["hp"], rng.counter))
        return [next(choices)]

    monkeypatch.setattr(game_state, '_resolve_debug_selection', select)
    event = KnowingSkull()
    event.trigger()
    assert game_state.drive_actions() is None
    draw = 0 if sozu else 1
    assert menus == [(100, 6, 0), (94, 7, draw), (87, 8, 2 * draw)]
    if full or sozu:
        assert list(player.potions) == originals
    else:
        assert [getattr(potion, "_original_potion_id", None) for potion in player.potions] == [
            "SteroidPotion", "Fire Potion",
        ]
    assert player.hp == 81 and event.potion_cost == 8 and event.event_ended


@pytest.mark.parametrize('language', ['en', 'zh'])
def test_skull_leave_text_and_actual_payment_agree(player, monkeypatch, language):
    set_language(language)
    player.hp = 7
    player.block = 100
    event = KnowingSkull()
    event.trigger()
    menu = queued_menu()
    assert '6' in resolve_text(menu.options[3].detail)
    game_state.action_queue.add_actions(menu.options[3].actions)
    assert game_state.drive_actions() is None
    assert player.hp == 1 and player.block == 100 and event.event_ended
