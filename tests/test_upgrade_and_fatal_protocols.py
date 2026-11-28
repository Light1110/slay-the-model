import pytest

from actions.display import InputRequestAction
from cards.colorless.hand_of_greed import HandOfGreed
from cards.colorless.ritual_dagger import RitualDagger
from cards.colorless.wound import Wound
from cards.ironclad.defend import Defend
from cards.ironclad.searing_blow import SearingBlow
from cards.watcher.lesson_learned import LessonLearned
from enemies.act2.bronze_orb import BronzeOrb
from engine.game_state import game_state
from engine.random_streams import StreamRandom
from events.shining_light import ShiningLight
from relics.global_relics.event import WarpedTongs
from tests.test_deferred_damage_protocols import play, prepare


@pytest.mark.parametrize("ascension", [14, 15])
@pytest.mark.parametrize("count", [0, 1, 2, 3])
def test_shining_light_upgrades_distinct_cards_with_one_shuffle(ascension, count):
    game_state.config.debug["select_type"] = "first"
    game_state.ascension = ascension
    player = game_state.player
    excluded = Defend()
    excluded.upgrade()
    candidates = [SearingBlow() for _ in range(count)]
    player.card_manager.piles["deck"] = [excluded, *candidates]
    before_hp = player.hp
    rng = game_state.random_streams["misc"]
    rng.seed(0)
    reference = StreamRandom(0)
    expected = candidates.copy()
    if expected:
        reference.shuffle(expected)

    ShiningLight().trigger()
    request = game_state.action_queue.queue[-1]
    assert isinstance(request, InputRequestAction)
    assert game_state.drive_actions() is None

    assert [card.upgrade_level for card in candidates] == [int(card in expected[:2]) for card in candidates]
    assert excluded.upgrade_level == 1
    assert rng.export_state() == reference.export_state()
    loss = int(player.max_hp * (0.30 if ascension == 15 else 0.20))
    assert player.hp == before_hp - (loss if count else 0)


@pytest.mark.parametrize("count", [0, 1, 3])
def test_warped_tongs_upgrades_a_combat_copy_after_draw(count):
    player, _, combat = prepare(role="defect")
    permanent = SearingBlow()
    player.card_manager.piles["deck"] = [permanent]
    candidates = [permanent.copy() for _ in range(count)]
    player.card_manager.piles["hand"] = candidates[:1]
    # A status remains ineligible even if an effect makes it upgradeable.
    wound = Wound()
    wound.upgradeable = True
    player.card_manager.piles["draw_pile"] = [wound, *reversed(candidates[1:])]
    player.base_draw_count = len(player.card_manager.piles["draw_pile"])
    player.relics.append(WarpedTongs())
    combat.combat_state.combat_turn = 1
    rng = game_state.random_streams["shuffle"]
    rng.seed(0)
    reference = StreamRandom(0)
    expected = candidates.copy()
    if expected:
        reference.shuffle(expected)

    combat._start_player_turn()
    assert rng.counter == 0
    assert game_state.drive_actions() is None

    assert rng.export_state() == reference.export_state()
    assert [card.upgrade_level for card in candidates] == [int(card in expected[:1]) for card in candidates]
    assert wound.upgrade_level == permanent.upgrade_level == 0
    player.card_manager.reset_for_combat()
    assert player.card_manager.piles["draw_pile"][0].upgrade_level == 0


@pytest.mark.parametrize("card_type", [HandOfGreed, RitualDagger, LessonLearned])
@pytest.mark.parametrize("upgraded", [False, True])
def test_fatal_rewards_exclude_bronze_orb(card_type, upgraded):
    player, enemies, _ = prepare()
    target = BronzeOrb()
    target.hp = 1
    enemies[0] = target
    candidate = Defend()
    player.card_manager.piles["deck"] = [candidate]
    card = card_type()
    if upgraded:
        card.upgrade()
    before_damage = card.damage
    before_gold = player.gold
    rng = game_state.random_streams["misc"]
    before_rng = rng.export_state()

    assert play(card) is None

    assert target.is_dead()
    assert card.damage == before_damage
    assert player.gold == before_gold
    assert candidate.upgrade_level == 0
    assert rng.export_state() == before_rng
