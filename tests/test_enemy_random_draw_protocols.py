"""Regressions for Bronze Orb selection and Gremlin Leader's shared AI stream."""
import pytest

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
from engine.combat import Combat
from engine.game_state import game_state


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
