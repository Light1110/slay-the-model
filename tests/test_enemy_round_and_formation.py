"""Regression checks for monster queue boundaries and later summons."""
from contextlib import ExitStack
from unittest.mock import patch

import pytest

from actions.combat_damage import DealDamageAction
from actions.watcher import SkipEnemyTurnAction
from enemies.act1.acid_slime import AcidSlimeL
from enemies.act1.cultist import Cultist
from enemies.act1.spike_slime import SpikeSlimeL, SpikeSlimeM
from enemies.act3.dagger import Dagger
from enemies.act3.darkling import Darkling
from enemies.act3.reptomancer import Reptomancer
from engine.random_streams import StreamRandom
from map import encounter_pool
from powers.definitions.corpse_explosion import CorpseExplosionPower
from powers.definitions.metallicize import MetallicizePower
from powers.definitions.poison import PoisonPower
from relics.global_relics.boss import PhilosophersStone
from tests.test_enemy_opening_lifecycle import environment


def run_turn(combat, state):
    combat._start_player_turn()
    state.drive_actions()
    combat._end_player_phase()
    return combat.execute_enemy_phase()


def test_reptomancer_consumes_both_constructor_rolls(monkeypatch):
    _, state = environment(19)
    hp_rng = StreamRandom(42)
    reference = StreamRandom(42)
    monkeypatch.setitem(state.random_streams.streams, "monster_hp", hp_rng)
    reference.randint(180, 190)
    assert Reptomancer().hp == reference.randint(190, 200) == 197
    assert hp_rng.counter == 2
    assert Dagger().hp == reference.randint(20, 25)
    assert hp_rng.export_state() == reference.export_state()


@pytest.mark.parametrize("with_stone", [False, True])
def test_darkling_revives_with_life_link_and_notifies_only_for_itself(with_stone):
    helper, state = environment(0)
    target, other = Darkling(), Darkling()
    if with_stone:
        state.player.relics.append(PhilosophersStone())
    combat = helper.start_combat([target, other])
    state.drive_actions()
    other_strength = other.strength
    DealDamageAction(target.hp, target, source=state.player, damage_type="attack").execute()
    state.drive_actions()
    assert target.half_dead

    run_turn(combat, state)
    run_turn(combat, state)
    assert target.hp == target.max_hp // 2
    assert not target.half_dead
    assert target.has_power("Life Link")
    assert target.strength == int(with_stone)
    assert other.strength == other_strength


def test_enemy_start_and_end_powers_are_group_phases():
    helper, state = environment(0)
    first, second = Cultist(), Cultist()
    combat = helper.start_combat([first, second])
    run_turn(combat, state)
    first.add_power(MetallicizePower(amount=5, owner=first))
    second.hp = 40
    second.block = 7
    second.add_power(PoisonPower(amount=3, owner=second))
    observations = []

    def observe(native):
        def execute():
            observations.append((second.hp, second.get_power("Poison").amount, second.block, first.block))
            return native()
        return execute

    with patch.object(first, "execute_intention", observe(first.execute_intention)):
        with patch.object(second, "execute_intention", observe(second.execute_intention)):
            run_turn(combat, state)
    assert observations == [(37, 2, 0, 0), (37, 2, 0, 0)]
    assert first.block == 5


def test_start_of_turn_death_can_remove_an_earlier_actor():
    helper, state = environment(0)
    first, second = Cultist(), Cultist()
    combat = helper.start_combat([first, second])
    run_turn(combat, state)
    first.hp, second.hp, second.max_hp = 15, 1, 20
    second.add_power(PoisonPower(amount=3, owner=second))
    second.add_power(CorpseExplosionPower(amount=1, owner=second))
    hp = state.player.hp
    run_turn(combat, state)
    assert first.is_dead() and second.is_dead()
    assert first.history_intentions == ["ritual"]
    assert state.player.hp == hp


def test_skipped_enemy_phase_leaves_start_and_end_powers_unresolved():
    helper, state = environment(0)
    enemy = Cultist()
    combat = helper.start_combat([enemy])
    enemy.add_power(PoisonPower(amount=3, owner=enemy))
    enemy.add_power(MetallicizePower(amount=5, owner=enemy))
    enemy.block = 7
    hp = enemy.hp
    SkipEnemyTurnAction().execute()
    run_turn(combat, state)
    assert (enemy.hp, enemy.block, enemy.get_power("Poison").amount) == (hp, 7, 3)
    assert not enemy.history_intentions


@pytest.mark.parametrize("with_other,delta", [(False, 0), (True, 2)])
def test_dagger_explosion_roll_only_runs_in_continuing_combat(with_other, delta, monkeypatch):
    helper, state = environment(19)
    rng = StreamRandom(0)
    monkeypatch.setitem(state.random_streams.streams, "ai", rng)
    dagger = Dagger()
    team = [dagger, Cultist()] if with_other else [dagger]
    combat = helper.start_combat(team)
    run_turn(combat, state)
    expected = StreamRandom(0)
    expected.restore_state(rng.export_state())
    for _ in range(delta):
        expected.randint(0, 99)
    run_turn(combat, state)
    assert dagger.history_intentions == ["Wound", "Explode"]
    assert dagger.is_dead()
    assert (dagger not in combat.enemies) == with_other
    assert rng.export_state() == expected.export_state()


@pytest.mark.parametrize("factory,draws", [(SpikeSlimeL, 3), (AcidSlimeL, 2)])
def test_only_large_spike_slime_rolls_after_both_split_children(factory, draws, monkeypatch):
    helper, state = environment(0)
    rng = StreamRandom(0)
    monkeypatch.setitem(state.random_streams.streams, "ai", rng)
    parent = factory()
    combat = helper.start_combat([parent])
    DealDamageAction(parent.hp - parent.max_hp // 2, parent, source=state.player).execute()
    state.drive_actions()
    expected = StreamRandom(0)
    expected.restore_state(rng.export_state())
    for _ in range(draws):
        expected.randint(0, 99)
    rolled = []
    select_child = SpikeSlimeM.determine_next_intention
    select_parent = parent.determine_next_intention

    def child_select(enemy, floor):
        rolled.append(enemy)
        return select_child(enemy, floor)

    def parent_select(floor):
        rolled.append(parent)
        return select_parent(floor)

    with patch.object(SpikeSlimeM, "determine_next_intention", child_select):
        with patch.object(parent, "determine_next_intention", parent_select):
            run_turn(combat, state)
    assert len(combat.enemies) == 2
    assert all(not child.history_intentions for child in combat.enemies)
    assert rolled == [*combat.enemies, parent] if factory is SpikeSlimeL else not rolled
    assert rng.export_state() == expected.export_state()


@pytest.mark.parametrize("factory,owner_index,positions", [
    (encounter_pool._create_bronze_automaton, 0, [-300, None, 200]),
    (encounter_pool._create_boss_collector, 0, [-470, -285, None]),
    (encounter_pool._create_gremlin_leader, 2, [-532, -366, -170, None]),
    (encounter_pool._create_reptomancer, 1, [-250, -220, None, 180, 210]),
])
def test_summons_insert_in_formation_and_act_in_that_order(factory, owner_index, positions):
    helper, state = environment(19)
    original = factory()
    owner = original[owner_index]
    combat = helper.start_combat(original.copy())
    if factory is encounter_pool._create_gremlin_leader:
        owner.current_intention = owner.intentions["Rally!"]
    run_turn(combat, state)
    assert [enemy.formation_position for enemy in combat.enemies] == positions
    assert all(not enemy.history_intentions for enemy in combat.enemies if enemy not in original)

    team = combat.enemies.copy()
    executed = []
    def observe(enemy):
        native = enemy.execute_intention

        def execute():
            executed.append(enemy)
            return native()

        return execute

    with ExitStack() as patches:
        for enemy in team:
            patches.enter_context(patch.object(enemy, "execute_intention", observe(enemy)))
        run_turn(combat, state)
    assert executed == team


@pytest.mark.parametrize("factory,owner_index,move,position", [
    (encounter_pool._create_boss_collector, 0, "Spawn", -285),
    (encounter_pool._create_gremlin_leader, 2, "Rally!", -366),
    (encounter_pool._create_reptomancer, 1, "Spawn Dagger", 210),
])
def test_resummon_fills_only_the_open_slot(factory, owner_index, move, position):
    helper, state = environment(19)
    initial = factory()
    owner = initial[owner_index]
    combat = helper.start_combat(initial.copy())
    owner.current_intention = owner.intentions[move]
    run_turn(combat, state)
    old = next(enemy for enemy in combat.enemies if enemy.formation_position == position)
    survivors = [enemy for enemy in combat.enemies if enemy is not old]
    combat.remove_enemy(old)

    owner.current_intention = owner.intentions[move]
    owner.execute_intention()
    state.drive_actions()
    newcomers = [enemy for enemy in combat.enemies if enemy not in survivors]
    assert len(newcomers) == 1
    assert newcomers[0].formation_position == position
    assert newcomers[0].current_intention is not None
    assert not newcomers[0].history_intentions
