"""Player card observers and Lagavulin's executed-turn state transitions."""
import pytest

from actions.combat import DealDamageAction, LoseHPAction
from cards.colorless.trip import Trip
from cards.ironclad.defend import Defend
from cards.ironclad.inflame import Inflame
from cards.ironclad.strike import Strike
from enemies.act1.gremlin_nob import GremlinNob
from enemies.act1.lagavulin import Lagavulin
from enemies.act2.taskmaster import Taskmaster
from engine.game_state import game_state
from engine.messages import CardPlayedMessage
from powers.base import Power
from powers.definitions.enrage import EnragePower
from powers.definitions.metallicize import MetallicizePower
from tests.test_combat_utils import create_test_helper


def finish_turn(combat):
    combat._end_player_phase()
    combat.execute_enemy_phase()


@pytest.mark.parametrize('ascension,amount', [(0, 2), (17, 2), (18, 3)])
def test_real_self_target_skill_only_triggers_enrage_after_bellow(ascension, amount):
    helper = create_test_helper()
    helper.create_player(energy=10)
    game_state.ascension = ascension
    nob = GremlinNob()
    combat = helper.start_combat([nob])
    first = Defend()
    helper.add_card_to_hand(first)
    assert helper.play_card(first)
    assert nob.strength == 0
    combat.execute_enemy_phase()  # The opening Bellow applies Enrage.
    assert nob.get_power('Enrage') is not None
    for number in (1, 2):
        card = Defend()
        helper.add_card_to_hand(card)
        assert helper.play_card(card)
        assert nob.strength == amount * number


@pytest.mark.parametrize('target_mode', ['other', 'nob', 'all'])
def test_real_targeted_and_all_target_skills_trigger_once_per_enraged_enemy(target_mode):
    helper = create_test_helper()
    helper.create_player()
    first, second = GremlinNob(), GremlinNob()
    other = Taskmaster()
    helper.start_combat([first, second, other])
    first.add_power(EnragePower(amount=2))
    second.add_power(EnragePower(amount=3))
    card = Trip()
    if target_mode == 'all':
        card.upgrade()
    helper.add_card_to_hand(card)
    assert helper.play_card(card, target=other if target_mode == 'other' else first)
    assert first.strength == 2
    assert second.strength == 3


@pytest.mark.parametrize('card_class', [Strike, Inflame])
def test_non_skill_cards_do_not_trigger_enrage(card_class):
    helper = create_test_helper()
    helper.create_player(energy=10)
    nob = GremlinNob()
    helper.start_combat([nob])
    nob.add_power(EnragePower(amount=2))
    card = card_class()
    helper.add_card_to_hand(card)
    assert helper.play_card(card, target=nob)
    assert nob.strength == 0


def test_observer_opt_in_deduplicates_targets_and_preserves_player_hooks():
    helper = create_test_helper()
    player = helper.create_player()
    nob, dead = GremlinNob(), GremlinNob()
    helper.start_combat([nob, dead])
    nob.add_power(EnragePower(amount=2))
    dead.add_power(EnragePower(amount=3))
    dead.hp = 0
    calls = []
    class CounterPower(Power):
        def on_card_play(self, card, targets):
            calls.append(self.owner)
    player.add_power(CounterPower())
    nob.add_power(CounterPower())
    message = CardPlayedMessage(card=Defend(), owner=player, targets=[player, nob, nob, dead])
    participants = game_state.runtime_context.message_participants_for_message(message)
    assert sum(power is nob.get_power('Enrage') for power in participants) == 1
    game_state.publish_message(message)
    game_state.drive_actions()
    assert nob.strength == 2
    assert dead.strength == 0
    assert calls.count(player) == 1
    assert calls.count(nob) == 1  # Existing target routing still works.
    calls.clear()
    game_state.publish_message(CardPlayedMessage(card=Defend(), owner=player, targets=[player]))
    game_state.drive_actions()
    assert calls == [player]  # Unmarked enemy powers are not broadcast recipients.
    assert nob.strength == 4
    game_state.publish_message(CardPlayedMessage(card=Defend(), owner=Taskmaster(), targets=[]))
    game_state.drive_actions()
    assert nob.strength == 4  # Enemy card messages do not broadcast to observers.
    assert dead.strength == 0


@pytest.mark.parametrize('ascension,damage,siphon', [(0, 18, 1), (3, 20, 1), (18, 20, 2)])
@pytest.mark.parametrize('start_awake', [False, True])
def test_real_sleep_and_awake_cycles_are_stable_under_repeated_queries(ascension, damage, siphon, start_awake):
    helper = create_test_helper()
    player = helper.create_player(hp=500, max_hp=500)
    game_state.ascension = ascension
    enemy = Lagavulin(start_awake=start_awake)
    combat = helper.start_combat([enemy])
    assert enemy.turns_without_damage == 0
    assert enemy.block == (0 if start_awake else 8)
    expected = (['siphon_soul', 'attack', 'attack'] * 2 if start_awake else
                ['sleep'] * 3 + ['attack', 'attack', 'siphon_soul', 'attack', 'attack', 'siphon_soul'])
    attacks = debuffs = 0
    for turn, name in enumerate(expected):
        combat._start_player_turn()
        game_state.drive_actions()
        assert enemy.current_intention is enemy.intentions[name]
        for _ in range(3):
            assert enemy.determine_next_intention() is enemy.intentions[name]
        if not start_awake and turn < 3:
            assert enemy.turns_without_damage == turn
            assert enemy.is_sleeping
        finish_turn(combat)
        attacks += int(name == 'attack')
        debuffs += int(name == 'siphon_soul')
        assert player.hp == 500 - attacks * damage
        assert player.strength == -debuffs * siphon
        dexterity = player.get_power('Dexterity')
        if debuffs:
            assert dexterity is not None
            assert dexterity.amount == -debuffs * siphon
        else:
            assert dexterity is None
        if not start_awake and turn == 2:
            assert enemy.turns_without_damage == 3
            assert not enemy.is_sleeping
            assert enemy.current_intention is enemy.intentions['attack']
            assert enemy.get_power('Metallicize') is None
            assert enemy.block == 0
    assert enemy.history_intentions == expected


@pytest.mark.parametrize('wake_turn', [1, 2, 3])
def test_damage_wake_requires_hp_loss_and_stuns_exactly_once(wake_turn):
    helper = create_test_helper()
    player = helper.create_player(hp=200, max_hp=200)
    enemy = Lagavulin()
    combat = helper.start_combat([enemy])
    for _ in range(wake_turn - 1):
        combat._start_player_turn()
        game_state.drive_actions()
        finish_turn(combat)
    combat._start_player_turn()
    game_state.drive_actions()
    hp = enemy.hp
    DealDamageAction(damage=8, target=enemy, source=player, damage_type='attack').execute()
    game_state.drive_actions()
    assert enemy.hp == hp
    assert enemy.is_sleeping
    assert enemy.current_intention is enemy.intentions['sleep']
    for _ in range(2):
        LoseHPAction(amount=1, target=enemy).execute()
        game_state.drive_actions()
        assert enemy.current_intention is enemy.intentions['stunned']
        assert enemy.determine_next_intention() is enemy.intentions['stunned']
    assert enemy.get_power('Metallicize') is None
    assert enemy.turns_without_damage == 0
    finish_turn(combat)
    assert player.hp == 200
    assert enemy.history_intentions.count('stunned') == 1
    for name in ('attack', 'attack', 'siphon_soul'):
        combat._start_player_turn()
        game_state.drive_actions()
        assert enemy.current_intention is enemy.intentions[name]
        finish_turn(combat)
    assert player.hp == 164
    assert player.strength == -1


@pytest.mark.parametrize('natural', [False, True])
def test_waking_removes_only_sleeping_metallicize_stacks(natural):
    helper = create_test_helper()
    helper.create_player()
    enemy = Lagavulin()
    helper.start_combat([enemy])
    enemy.add_power(MetallicizePower(amount=5))
    if natural:
        for _ in range(3):
            enemy.on_player_turn_start()
            enemy.execute_intention()
    else:
        LoseHPAction(amount=1, target=enemy).execute()
        game_state.drive_actions()
    metallicize = enemy.get_power('Metallicize')
    assert metallicize is not None
    assert metallicize.amount == 5
