"""INT-001: an opening selection is used once, without a second RNG roll."""
import random
import pytest

from enemies import act1, act2, act3
from enemies.act1.cultist import Cultist
from enemies.act1.gremlin_nob import GremlinNob
from enemies.act1.looter import Looter
from enemies.act1.sentry import Sentry
from enemies.act1.slime_boss import SlimeBoss
from enemies.act1.the_guardian import TheGuardian
from enemies.act2.bronze_automaton import BronzeAutomaton
from enemies.act2.bronze_orb import BronzeOrb
from enemies.act2.chosen import Chosen
from enemies.act2.mugger import Mugger
from enemies.act2.byrd import Byrd
from enemies.act2.mystic import Mystic
from enemies.act2.snake_plant import SnakePlant
from enemies.act2.spheric_guardian import SphericGuardian
from enemies.act2.the_champ import TheChamp
from enemies.act2.the_collector import TheCollector
from enemies.act3.dagger import Dagger
from enemies.act3.darkling import Darkling
from enemies.act3.deca import Deca
from enemies.act3.donu import Donu
from enemies.act3.exploder import Exploder
from enemies.act3.giant_head import GiantHead
from enemies.act3.nemesis import Nemesis
from enemies.act3.the_maw import TheMaw
from enemies.act4.corrupt_heart import CorruptHeart
from enemies.act4.spire_shield import SpireShield
from enemies.act4.spire_spear import SpireSpear
from actions.combat import EndTurnAction
from actions.watcher import SkipEnemyTurnAction
from engine.combat import Combat
from engine.random_streams import StreamRandom, get_rng
from tests.test_combat_utils import create_test_helper


def environment(ascension):
    helper = create_test_helper()
    player = helper.create_player(hp=10000, max_hp=10000)
    player.base_draw_count = 0
    gs = helper.game_state
    gs.ascension = ascension
    random.seed(829)
    return helper, gs


FACTORIES = [Cultist, GremlinNob, Sentry, SlimeBoss, TheGuardian,
             BronzeAutomaton, BronzeOrb, Chosen, Mystic, SnakePlant,
             SphericGuardian, TheChamp, TheCollector, Dagger, Darkling,
             Deca, Donu, Exploder, GiantHead, Nemesis, TheMaw,
             CorruptHeart, SpireShield, SpireSpear, Byrd]

ROSTER = [
    getattr(act, name)
    for act in (act1, act2, act3)
    for name in act.__all__
] + [Looter, TheMaw, CorruptHeart, SpireShield, SpireSpear]


@pytest.mark.parametrize("factory", ROSTER)
@pytest.mark.parametrize("ascension", [0, 17, 19])
@pytest.mark.parametrize("run_seed", [0, 1, 42])
def test_roster_opening_starts_with_one_primary_ai_roll(monkeypatch, factory, ascension, run_seed):
    helper, gs = environment(ascension)
    rng = StreamRandom(run_seed)
    monkeypatch.setitem(gs.random_streams.streams, "ai", rng)
    calls = []
    integer = rng.random_int

    def observe(start, end=None):
        calls.append((start, end, rng.counter))
        return integer(start, end)

    monkeypatch.setattr(rng, "random_int", observe)
    enemy = factory()
    combat = helper.start_combat([enemy])
    assert calls[0] == (0, 99, 0)
    assert enemy.current_intention is not None
    selection = enemy.current_intention
    state = rng.export_state()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is selection
    assert rng.export_state() == state


@pytest.mark.parametrize("factory", FACTORIES)
@pytest.mark.parametrize("ascension", [0, 19])
def test_first_player_turn_preserves_selection_and_rng(factory, ascension, monkeypatch):
    helper, gs = environment(ascension)
    enemy = factory()
    calls = []
    native = enemy.determine_next_intention

    def select(*args, **kwargs):
        calls.append(1)
        return native(*args, **kwargs)

    monkeypatch.setattr(enemy, 'determine_next_intention', select)
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    before = enemy.current_intention
    rng = random.getstate()
    assert len(calls) == 1
    combat._start_player_turn()
    gs.drive_actions()
    assert len(calls) == 1
    assert enemy.current_intention is before
    assert random.getstate() == rng


@pytest.mark.parametrize("factory,expected", [
    (Donu, ['Circle of Power', 'Beam', 'Circle of Power', 'Beam']),
    (Deca, ['Beam', 'Square of Protection', 'Beam', 'Square of Protection']),
    (SphericGuardian, ['activate', 'debuff_attack', 'slam', 'harden']),
])
@pytest.mark.parametrize('ascension', [0, 19])
def test_selected_opening_is_not_repeated_next_round(factory, expected, ascension):
    helper, gs = environment(ascension)
    enemy = factory()
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    actual = []
    for _ in range(4):
        combat._start_player_turn()
        gs.drive_actions()
        assert enemy.current_intention is not None
        actual.append(enemy.current_intention.name)
        combat._end_player_phase()
        combat.execute_enemy_phase()
    assert actual == expected


@pytest.mark.parametrize('ascension', [0, 19])
def test_three_sentries_keep_position_openings_then_alternate(ascension):
    helper, gs = environment(ascension)
    enemies = [Sentry(is_middle=False), Sentry(is_middle=True), Sentry(is_middle=False)]
    combat = helper.start_combat(enemies)
    gs.drive_actions()
    for wanted in [['bolt', 'beam', 'bolt'], ['beam', 'bolt', 'beam']]:
        combat._start_player_turn()
        gs.drive_actions()
        assert [e.current_intention.name for e in enemies] == wanted
        combat._end_player_phase()
        combat.execute_enemy_phase()


def test_skipping_enemy_turn_does_not_advance_the_unexecuted_opening():
    helper, gs = environment(0)
    enemy = Sentry()
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    combat._start_player_turn()
    gs.drive_actions()
    opening = enemy.current_intention
    SkipEnemyTurnAction().execute()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is opening
    assert enemy.turn_count == 1
    combat._end_player_phase()
    combat.execute_enemy_phase()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is not opening
    assert enemy.turn_count == 2


def test_helper_enemy_phase_before_first_player_phase_does_not_freeze_next_selection():
    helper, gs = environment(0)
    enemy = Sentry()
    combat = helper.start_combat([enemy])
    gs.drive_actions()
    opening = enemy.current_intention
    combat.execute_enemy_phase()
    combat._start_player_turn()
    gs.drive_actions()
    assert enemy.current_intention is not opening


def test_bronze_automaton_actually_summons_at_first_enemy_action():
    helper, gs = environment(0)
    boss = BronzeAutomaton()
    combat = helper.start_combat([boss])
    gs.drive_actions()
    combat._start_player_turn()
    gs.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    orbs = [e for e in combat.enemies if isinstance(e, BronzeOrb)]
    assert len(orbs) == 2
    assert all(not orb.history_intentions for orb in orbs)
    combat._start_player_turn()
    gs.drive_actions()
    combat._end_player_phase()
    combat.execute_enemy_phase()
    assert all(len(orb.history_intentions) == 1 for orb in orbs)


def test_native_combat_start_shows_fixed_opening_at_first_decision(monkeypatch):
    helper, gs = environment(0)
    enemy = GremlinNob()
    combat = Combat([enemy])
    seen = []

    class FirstDecisionReached(Exception):
        pass

    def choose(req):
        seen.append(enemy.current_intention.name)
        # Observe the original Combat.start boundary without changing AI,
        # effects or fabricating a combat result.
        raise FirstDecisionReached

    monkeypatch.setattr(gs, 'resolve_input_request', choose)
    with pytest.raises(FirstDecisionReached):
        combat.start()
    assert seen == ['bellow']


@pytest.mark.parametrize("ascension,expected", [
    (16, ["poke", "hex", "debilitate", "zap"]),
    (17, ["hex", "debilitate", "zap", "debilitate"]),
])
def test_chosen_selects_once_after_each_turn(monkeypatch, ascension, expected):
    helper, gs = environment(ascension)
    rng = get_rng("ai")
    monkeypatch.setattr(rng, "randint", lambda _start, _end: 39)
    enemy = Chosen()
    combat = helper.start_combat([enemy])
    for move in expected:
        combat._start_player_turn()
        gs.drive_actions()
        assert enemy.current_intention.name == move
        combat._end_player_phase()
        combat.execute_enemy_phase()


@pytest.mark.parametrize("factory", [Looter, Mugger])
@pytest.mark.parametrize("use_smoke", [False, True])
def test_thieves_mug_twice_then_flee(monkeypatch, factory, use_smoke):
    helper, gs = environment(17)
    rng = get_rng("ai")
    monkeypatch.setattr(rng, "random_boolean", lambda chance: use_smoke)
    thief = factory()
    combat = helper.start_combat([thief])
    expected = ["mug", "mug"]
    if not use_smoke:
        expected.append("lunge")
    expected.extend(["smoke_bomb", "escape"])
    for move in expected:
        combat._start_player_turn()
        gs.drive_actions()
        assert thief.current_intention.name == move
        combat._end_player_phase()
        combat.execute_enemy_phase()
    assert thief not in combat.enemies


@pytest.mark.parametrize("ascension", [0, 17, 18, 19])
def test_shield_and_spear_share_ai_stream_in_enemy_order(monkeypatch, ascension):
    from cards.colorless.burn import Burn

    helper, gs = environment(ascension)
    gs.player.base_orb_slots = 0
    rng = StreamRandom(0)
    monkeypatch.setitem(gs.random_streams.streams, "ai", rng)
    shield, spear = SpireShield(), SpireSpear()
    combat = helper.start_combat([shield, spear])
    gs.drive_actions()

    expected = StreamRandom(0)
    expected.randint(0, 99)
    shield_opening = "Fortify" if expected.random_boolean() else "Bash"
    expected.randint(0, 99)
    assert shield.current_intention.name == shield_opening
    assert spear.current_intention.name == "Burn Strike"
    assert rng.export_state() == expected.export_state()
    for enemy in (shield, spear):
        assert enemy.get_power("Artifact").amount == (2 if ascension >= 18 else 1)

    for _ in range(2):
        combat._start_player_turn()
        gs.drive_actions()
        combat._end_player_phase()
        assert combat.execute_enemy_phase() is None
        expected.randint(0, 99)
        expected.randint(0, 99)
    expected_spear = "Piercer" if expected.random_boolean() else "Burn Strike"
    assert shield.current_intention.name == "Smash"
    assert spear.current_intention.name == expected_spear
    assert shield.history_intentions == [shield_opening, "Fortify" if shield_opening == "Bash" else "Bash"]
    assert spear.history_intentions == ["Burn Strike", "Skewer"]
    assert rng.export_state() == expected.export_state()
    burn_pile = "draw_pile" if ascension >= 18 else "discard_pile"
    assert sum(isinstance(card, Burn) for card in gs.player.card_manager.get_pile(burn_pile)) == 2


@pytest.mark.parametrize("ascension,count", [(17, 1), (18, 2)])
def test_reptomancer_elite_spawns_daggers_that_act_next_turn(monkeypatch, ascension, count):
    from enemies.act3.reptomancer import Reptomancer
    from map.encounter_pool import EncounterPool
    from utils.types import EnemyType

    helper, gs = environment(ascension)
    pool = EncounterPool(seed=42, act_id=3)
    monkeypatch.setattr(pool, "_select_weighted_encounter", lambda _available: "Reptomancer")
    enemies, name = pool.get_elite_encounter(8)
    assert name == "Reptomancer"
    left, leader, right = enemies
    assert isinstance(leader, Reptomancer) and leader.enemy_type is EnemyType.ELITE
    assert isinstance(left, Dagger) and isinstance(right, Dagger)
    combat = helper.start_combat(enemies)
    gs.drive_actions()

    combat._start_player_turn()
    gs.drive_actions()
    combat._end_player_phase()
    assert combat.execute_enemy_phase() is None
    spawned = [enemy for enemy in combat.enemies if enemy not in (left, leader, right)]
    assert len(spawned) == count
    assert all(enemy.current_intention.name == "Wound" and not enemy.history_intentions for enemy in spawned)

    combat._start_player_turn()
    gs.drive_actions()
    combat._end_player_phase()
    assert combat.execute_enemy_phase() is None
    assert all(enemy.history_intentions == ["Wound"] for enemy in spawned)
    assert left not in combat.enemies
    assert len(leader.history_intentions) == 2


@pytest.mark.parametrize("ascension", [0, 17])
def test_gremlin_wizard_uses_three_charges_and_high_ascension_repeats_blast(ascension):
    helper, gs = environment(ascension)
    wizard = act1.GremlinWizard()
    combat = helper.start_combat([wizard])
    charge = "gremlin_wizard_charge"
    blast = "gremlin_wizard_ultimate_blast"
    for expected in (charge, charge, charge, blast, blast if ascension >= 17 else charge):
        combat._start_player_turn()
        gs.drive_actions()
        assert wizard.current_intention.name == expected
        combat._end_player_phase()
        assert combat.execute_enemy_phase() is None


@pytest.mark.parametrize("ascension,threshold", [(0, 30), (9, 35), (19, 40)])
def test_guardian_switches_current_intent_when_damage_reaches_threshold(ascension, threshold):
    from actions.combat_damage import DealDamageAction

    helper, gs = environment(ascension)
    guardian = TheGuardian()
    combat = helper.start_combat([guardian])
    gs.drive_actions()
    assert guardian.current_intention.name == "charging_up"
    DealDamageAction(threshold - 1, guardian, source=gs.player).execute()
    gs.drive_actions()
    assert guardian.current_intention.name == "charging_up"
    DealDamageAction(1, guardian, source=gs.player).execute()
    gs.drive_actions()
    assert guardian.current_intention.name == "defensive_mode"
    assert guardian.block == 20
    combat.execute_enemy_phase()
    assert guardian.history_intentions == ["defensive_mode"]
    assert guardian.current_intention.name == "roll_attack"


@pytest.mark.parametrize("ascension,next_move", [(17, "Stunned"), (18, "Stunned"), (19, "Boost")])
def test_automaton_changes_hyper_beam_followup_at_a19(ascension, next_move):
    helper, gs = environment(ascension)
    enemy = BronzeAutomaton()
    combat = helper.start_combat([enemy])
    for move in ("Spawn Orbs", "Flail", "Boost", "Flail", "Boost", "Hyper Beam"):
        combat._start_player_turn()
        gs.drive_actions()
        assert enemy.current_intention.name == move
        combat._end_player_phase()
        assert combat.execute_enemy_phase() is None
    assert enemy.current_intention.name == next_move
