"""Regressions for enemy random draws and action ordering."""
import pytest

from actions.combat import RollEnemyIntentionAction
from cards.colorless.clumsy import Clumsy
from cards.colorless.doubt import Doubt
from cards.ironclad.defend import Defend
from cards.ironclad.feed import Feed
from cards.ironclad.impervious import Impervious
from cards.ironclad.reaper import Reaper
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from enemies.act2.bronze_orb import BronzeOrb
from enemies.act2.gremlin_leader import GremlinLeader
from enemies.act3.exploder import Exploder
from engine.combat import Combat
from engine.game_state import game_state
from map.encounter_pool import _create_darkling
from utils.result_types import GameTerminalState


@pytest.mark.parametrize("pile_name", ["draw_pile", "discard_pile"])
def test_stasis_steals_from_sorted_tier_without_reordering_the_source(pile_name):
    reaper, feed, impervious = Reaper(), Feed(), Impervious()
    piles = game_state.player.card_manager.piles
    piles["draw_pile"] = []
    piles["discard_pile"] = []
    piles[pile_name] = [reaper, feed, impervious]
    orb = BronzeOrb()
    rng = game_state.random_streams["card_random"]
    rng.seed(0)

    orb.current_intention = orb.intentions["Steal"]
    orb.execute_intention()

    assert orb.stolen_cards == [impervious]
    assert piles[pile_name] == [reaper, feed]
    assert rng.counter == 1
    assert rng.randint(0, 999) == 960


def test_stasis_fallback_includes_nonbasic_cards_and_prefers_the_draw_pile():
    strike, defend, doubt, clumsy = Strike(), Defend(), Doubt(), Clumsy()
    discarded = Feed()
    piles = game_state.player.card_manager.piles
    piles["draw_pile"] = [strike, defend, doubt, clumsy]
    piles["discard_pile"] = [discarded]
    orb = BronzeOrb()
    rng = game_state.random_streams["card_random"]
    rng.seed(1)

    orb.intentions["Steal"].execute()

    assert orb.stolen_cards == [clumsy]
    assert piles["draw_pile"] == [strike, defend, doubt]
    assert piles["discard_pile"] == [discarded]
    assert rng.counter == 1


def test_stasis_preserves_duplicate_order_and_card_identity():
    first, second, reaper = Feed(), Feed(), Reaper()
    piles = game_state.player.card_manager.piles
    piles["draw_pile"] = [reaper, first, second]
    orb = BronzeOrb()
    game_state.random_streams["card_random"].seed(0)

    orb.intentions["Steal"].execute()

    assert orb.stolen_cards[0] is second
    assert piles["draw_pile"] == [reaper, first]


def test_stasis_does_not_draw_when_both_piles_are_empty():
    piles = game_state.player.card_manager.piles
    piles["draw_pile"] = []
    piles["discard_pile"] = []
    orb = BronzeOrb()
    rng = game_state.random_streams["card_random"]
    before = rng.export_state()

    orb.intentions["Steal"].execute()

    assert not orb.stolen_cards
    assert rng.export_state() == before


def test_gremlin_leader_encourage_consumes_ai_before_next_intention():
    ally = Cultist()
    ally.is_minion = True
    leader = GremlinLeader()
    combat = Combat(enemies=[ally, leader])
    combat._init_combat()
    assert game_state.drive_actions() is None
    rng = game_state.random_streams["ai"]
    rng.seed(1)

    leader.current_intention = leader.intentions["Encourage"]
    leader.execute_intention()
    assert rng.counter == 1
    assert game_state.drive_actions() is None
    leader.advance_intention_after_turn(20)

    assert leader.current_intention is leader.intentions["Rally!"]
    assert rng.counter == 2
    assert rng.randint(0, 999) == 188


@pytest.mark.parametrize(("ascension", "hp", "nip"), [
    (1, [52, 48, 48], [7, 9, 10]),
    (2, [52, 48, 48], [9, 11, 12]),
    (6, [52, 48, 48], [9, 11, 12]),
    (7, [52, 52, 51], [9, 11, 12]),
])
def test_darkling_factory_rolls_hp_then_nip_at_each_ascension_boundary(ascension, hp, nip):
    game_state.ascension = ascension
    rng = game_state.random_streams["monster_hp"]
    rng.seed(0)

    enemies = _create_darkling()

    assert [enemy.hp for enemy in enemies] == hp
    assert [enemy.intentions["Nip"].base_damage for enemy in enemies] == nip
    assert rng.counter == 6
    assert rng.randint(0, 999) == 442


@pytest.mark.parametrize("survivor", [False, True])
def test_exploder_rolls_before_dying_even_as_the_last_enemy(survivor, monkeypatch):
    game_state.ascension = 0
    game_state.player.relics.clear()
    rng = game_state.random_streams["ai"]
    rng.seed(0)
    exploder = Exploder()
    combat = Combat(enemies=[exploder, Cultist()] if survivor else [exploder])
    combat._init_combat()
    assert game_state.drive_actions() is None

    for _ in range(2):
        assert combat.execute_enemy_phase() is None
    assert rng.counter == (6 if survivor else 3)
    assert exploder.current_intention is exploder.intentions["Explode"]
    health_at_roll = []
    original = RollEnemyIntentionAction.execute

    def observe_roll(action):
        health_at_roll.append(action.enemy.hp)
        original(action)

    monkeypatch.setattr(RollEnemyIntentionAction, "execute", observe_roll)
    assert combat.execute_enemy_phase() is None
    assert health_at_roll == [exploder.max_hp]
    assert exploder.is_dead()
    assert rng.counter == (8 if survivor else 4)
    assert rng.randint(0, 999) == (179 if survivor else 231)
    assert combat._check_combat_end() == (None if survivor else GameTerminalState.COMBAT_WIN)
