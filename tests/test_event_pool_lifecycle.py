"""Regression coverage for event branching, run isolation and real elapsed time."""
import random
import importlib
from unittest.mock import patch

import pytest

from engine.game_state import game_state
from engine.run_clock import RunClock
from events.event_pool import EventPool
from events.secret_portal import SecretPortal
from events.the_cleric import TheClericEvent


class DummyEvent:
    pass


@pytest.mark.parametrize(('roll', 'expected'), [(0.24999, 'shrine'), (0.25, 'event')])
def test_shrine_branch_boundary(roll: float, expected: str):
    rng = random.Random(7)
    pool = EventPool(rng=rng)
    for category in ('event', 'shrine'):
        pool.register_event(DummyEvent, category, category=category)
    with patch.object(rng, 'random', return_value=roll):
        selected = pool.draw_metadata()
    assert selected is not None
    assert selected.event_id == expected


@pytest.mark.parametrize('category', ['event', 'shrine', 'special'])
def test_empty_branch_falls_back_and_consumption_lifecycle(category: str):
    pool = EventPool()
    pool.register_event(DummyEvent, 'only', category=category)
    assert pool.get_random_event(1) is DummyEvent
    assert pool.get_random_event(1) is None
    assert pool.get_random_event(2) is (None if category == 'special' else DummyEvent)
    pool.reset_unique_events()
    assert pool.get_random_event(1) is DummyEvent


def test_conditions_do_not_consume_and_excluded_events_never_draw():
    enabled = False
    pool = EventPool()
    pool.register_event(DummyEvent, 'temporary', requires_condition=lambda: enabled)
    pool.register_event(DummyEvent, 'excluded', category='excluded')
    pool.register_event(DummyEvent, 'zero', weight=0)
    assert pool.draw_metadata() is None
    enabled = True
    assert [m.event_id for m in pool.get_available_events()] == ['temporary']
    assert pool.get_random_event() is DummyEvent
    assert pool.draw_metadata() is None


def test_seed_is_independent_of_registration_order_and_global_random():
    def draw(reverse: bool):
        pool = EventPool(seed=42)
        ids = list('abcdefgh')
        for key in reversed(ids) if reverse else ids:
            pool.register_event(DummyEvent, key)
        sequence = []
        for _ in ids:
            random.random()
            selected = pool.draw_metadata()
            assert selected is not None
            sequence.append(selected.event_id)
        return sequence
    assert draw(False) == draw(True)


def test_batch_api_uses_same_draw_and_stops_at_empty_pool():
    pool = EventPool()
    pool.register_event(DummyEvent, 'only')
    from utils.random import get_random_events
    with patch.object(importlib.import_module('events.event_pool'), 'event_pool', pool):
        assert len(get_random_events(1, 4)) == 1
        assert get_random_events(1, 1) == []


def test_clock_waiting_stop_and_reset():
    now = [100.0]
    clock = RunClock(lambda: now[0])
    assert clock.elapsed == 0
    clock.start()
    now[0] += 799
    clock.start()
    assert clock.elapsed == 799
    clock.stop()
    now[0] += 10
    assert clock.elapsed == 799
    clock.start()
    now[0] += 1
    assert clock.elapsed == 800
    clock.reset()
    assert clock.elapsed == 0


def test_run_reset_and_chapter_transition_preserve_only_special_usage():
    now = [0.0]
    game_state.run_clock = RunClock(lambda: now[0])
    game_state.begin_run()
    state = game_state.event_pool_state
    state.used_in_act.add('ordinary')
    state.used_once.add('special')
    now[0] = 800
    game_state.current_act = 2
    game_state.initialize_map()
    assert state.used_in_act == set()
    assert state.used_once == {'special'}
    assert game_state.elapsed_time == 800
    game_state.begin_run()
    assert state.used_once == set()
    assert game_state.elapsed_time == 0


def test_portal_and_cleric_thresholds():
    game_state.current_act = 3
    game_state.elapsed_time = 799
    assert not SecretPortal.can_appear()
    game_state.elapsed_time = 800
    assert SecretPortal.can_appear()
    game_state.current_act = 2
    assert not SecretPortal.can_appear()
    game_state.player.gold = 34
    assert not TheClericEvent.can_appear()
    game_state.player.gold = 35
    assert TheClericEvent.can_appear()


def test_colosseum_uses_strict_original_map_midpoint():
    from events.the_colosseum import TheColosseum
    game_state.current_act = 2
    game_state.initialize_map()
    data = game_state.map_data
    assert data is not None
    data.set_current_position(8, 0)
    assert not TheColosseum.can_appear()
    data.set_current_position(9, 0)
    assert TheColosseum.can_appear()
    game_state.current_act = 1
    assert not TheColosseum.can_appear()


@pytest.mark.parametrize(('ascension', 'highest', 'daily', 'expected'), [
    (0, 0, False, True), (0, 20, True, False), (1, 0, False, False),
    (14, 14, False, False), (14, 15, False, True), (15, 20, False, False),
])
def test_note_unlock_conditions(ascension: int, highest: int, daily: bool, expected: bool):
    from events.a_note_for_yourself import ANoteForYourself
    game_state.ascension = ascension
    game_state.config.daily_run = daily
    game_state.config.highest_unlocked_ascension = {game_state.player.namespace.lower(): highest}
    assert ANoteForYourself.can_appear() is expected
