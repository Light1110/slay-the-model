"""Card block modifiers, debuff stack display, and Feed minion kills."""

from actions.combat_cards import PlayCardBHAction
from cards.ironclad.defend import Defend
from cards.ironclad.feed import Feed
from cards.silent.dodge_and_roll import DodgeAndRoll
from enemies.act1.cultist import Cultist
from enemies.act2.the_collector import TorchHead
from orbs.frost import FrostOrb
from powers.definitions.after_image import AfterImagePower
from powers.definitions.dexterity import DexterityPower
from powers.definitions.frail import FrailPower
from powers.definitions.metallicize import MetallicizePower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper
from utils.dynamic_values import resolve_card_block


def _setup(energy=3):
    helper = create_test_helper()
    player = helper.create_player(hp=80, energy=energy)
    enemy = helper.create_enemy(Cultist, hp=50)
    helper.start_combat([enemy])
    return helper, player, enemy


def test_card_block_adds_dexterity_then_frail_once():
    helper, player, _enemy = _setup()
    player.add_power(DexterityPower(amount=3))
    card = Defend()

    assert resolve_card_block(card) == 8
    PlayCardBHAction(card, [player]).execute()
    helper.game_state.drive_actions()
    assert player.block == 8

    player.block = 0
    player.add_power(FrailPower(duration=2))
    frail_card = Defend()
    assert resolve_card_block(frail_card) == 6
    PlayCardBHAction(frail_card, [player]).execute()
    helper.game_state.drive_actions()
    assert player.block == 6


def test_frail_without_dexterity_floors_card_block():
    _, player, _enemy = _setup()
    player.add_power(FrailPower(duration=2))

    assert resolve_card_block(Defend()) == 3


def test_metallicize_after_image_and_frost_ignore_dexterity_and_frail():
    helper, player, _enemy = _setup()
    player.add_power(DexterityPower(amount=2))
    player.add_power(FrailPower(duration=2))
    player.add_power(MetallicizePower(amount=3))
    player.add_power(AfterImagePower(amount=1))

    player.get_power("Metallicize").on_turn_end()
    helper.game_state.drive_actions()
    assert player.block == 3

    player.block = 0
    player.get_power("After Image").on_card_play(Defend(), [])
    helper.game_state.drive_actions()
    assert player.block == 1

    player.block = 0
    FrostOrb().on_passive()
    helper.game_state.drive_actions()
    assert player.block == 2


def test_dodge_and_roll_snapshots_next_turn_block():
    helper, player, _enemy = _setup()
    player.add_power(DexterityPower(amount=3))

    PlayCardBHAction(DodgeAndRoll(), [player]).execute()
    helper.game_state.drive_actions()

    assert player.block == 7
    next_block = player.get_power("Next Turn Block")
    assert next_block is not None
    assert next_block.amount == 7

    player.get_power("Dexterity").amount = 0
    player.block = 0
    next_block.on_turn_start()
    helper.game_state.drive_actions()
    assert player.block == 7


def test_duration_debuffs_show_stacked_turns():
    _, _player, enemy = _setup()
    enemy.add_power(VulnerablePower(amount=2, duration=2, owner=enemy))
    enemy.add_power(VulnerablePower(amount=2, duration=2, owner=enemy))
    vulnerable = enemy.get_power("Vulnerable")
    assert vulnerable is not None
    assert vulnerable.amount == 4

    vulnerable.on_round_end()
    assert vulnerable.amount == 3

    enemy.add_power(WeakPower(amount=2, duration=2, owner=enemy))
    enemy.add_power(WeakPower(amount=1, duration=1, owner=enemy))
    weak = enemy.get_power("Weak")
    assert weak is not None
    assert weak.amount == 3

    enemy.add_power(FrailPower(amount=1, duration=1, owner=enemy))
    enemy.add_power(FrailPower(amount=2, duration=2, owner=enemy))
    frail = enemy.get_power("Frail")
    assert frail is not None
    assert frail.amount == 3


def test_feed_skips_minions_and_other_cards():
    helper, player, enemy = _setup()
    feed = Feed()
    other = Feed()
    starting_max_hp = player.max_hp

    feed.on_fatal(10, enemy, card=other)
    helper.game_state.drive_actions()
    assert player.max_hp == starting_max_hp

    feed.on_fatal(10, TorchHead(), card=feed)
    helper.game_state.drive_actions()
    assert player.max_hp == starting_max_hp

    feed.on_fatal(10, enemy, card=feed)
    helper.game_state.drive_actions()
    assert player.max_hp == starting_max_hp + 3
