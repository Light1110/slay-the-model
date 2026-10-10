"""Damage types, single floor, flying, and pen nib preview."""

from actions.combat import DealDamageAction, LoseHPAction
from actions.combat_cards import PlayCardBHAction
from cards.ironclad.defend import Defend
from cards.ironclad.strike import Strike
from cards.ironclad.twin_strike import TwinStrike
from cards.ironclad.whirlwind import Whirlwind
from enemies.act1.cultist import Cultist
from powers.definitions.back_attack import BackAttackPower
from powers.definitions.flying import FlyingPower
from powers.definitions.intangible import IntangiblePower
from powers.definitions.pen_nib import PenNibPower
from powers.definitions.strength import StrengthPower
from powers.definitions.thorns import ThornsPower
from powers.definitions.vulnerable import VulnerablePower
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper
from utils.dynamic_values import resolve_card_damage, resolve_potential_damage
from utils.types import DamageType, StatusType


def _setup(hp=80, energy=3):
    helper = create_test_helper()
    player = helper.create_player(hp=hp, energy=energy)
    enemy = helper.create_enemy(Cultist, hp=50)
    helper.start_combat([enemy])
    return helper, player, enemy


def test_weak_and_vulnerable_floor_once():
    _, player, enemy = _setup()
    player.add_power(WeakPower(duration=2))
    enemy.add_power(VulnerablePower(duration=2))

    assert resolve_potential_damage(10, player, enemy, damage_type=DamageType.PHYSICAL) == 11


def test_strength_then_weak_is_independent_of_apply_order():
    _, player, enemy = _setup()
    player.add_power(WeakPower(duration=2))
    player.add_power(StrengthPower(amount=3))
    weak_first = resolve_potential_damage(8, player, enemy, damage_type=DamageType.PHYSICAL)

    player.powers.clear()
    player.add_power(StrengthPower(amount=3))
    player.add_power(WeakPower(duration=2))
    strength_first = resolve_potential_damage(8, player, enemy, damage_type=DamageType.PHYSICAL)

    assert weak_first == 8
    assert strength_first == 8


def test_pen_nib_multiplies_after_strength_and_preview_keeps_the_power():
    _, player, enemy = _setup()
    player.add_power(PenNibPower())
    player.add_power(StrengthPower(amount=3))
    card = Strike()

    assert resolve_potential_damage(10, player, enemy, card=card, damage_type=DamageType.PHYSICAL) == 26
    assert resolve_card_damage(card, target=enemy) == 18
    assert player.get_power("PenNib") is not None


def test_pen_nib_applies_before_weak():
    _, player, enemy = _setup()
    player.add_power(WeakPower(duration=2))
    player.add_power(PenNibPower())
    card = Strike()

    assert resolve_potential_damage(10, player, enemy, card=card, damage_type=DamageType.PHYSICAL) == 15
    assert player.get_power("PenNib") is not None


def test_divinity_stays_float_until_the_final_floor():
    _, player, enemy = _setup()
    player.status_manager.status = StatusType.DIVINITY
    player.add_power(WeakPower(duration=2))

    assert resolve_potential_damage(10, player, enemy, damage_type=DamageType.PHYSICAL) == 22


def test_back_attack_rounds_after_strength():
    _, player, enemy = _setup()
    enemy.add_power(BackAttackPower())
    enemy.add_power(StrengthPower(amount=3))

    assert resolve_potential_damage(10, enemy, player, damage_type=DamageType.PHYSICAL) == 19


def test_flying_halves_attack_after_vulnerable_and_before_intangible():
    _, player, enemy = _setup()
    enemy.add_power(FlyingPower(amount=3))

    assert resolve_potential_damage(10, player, enemy, damage_type=DamageType.PHYSICAL) == 5
    assert resolve_card_damage(Strike(), target=enemy) == 3
    assert enemy.get_power("Flying").amount == 3

    enemy.add_power(VulnerablePower(duration=2))
    assert resolve_potential_damage(10, player, enemy, damage_type=DamageType.PHYSICAL) == 7

    enemy.add_power(IntangiblePower(duration=1))
    assert resolve_potential_damage(10, player, enemy, damage_type=DamageType.PHYSICAL) == 1
    assert enemy.get_power("Flying").amount == 3


def test_flying_and_strength_do_not_change_thorns_or_hp_loss():
    helper, player, enemy = _setup()
    player.add_power(ThornsPower(amount=3))
    player.add_power(StrengthPower(amount=5))
    enemy.add_power(FlyingPower(amount=2))
    enemy.add_power(VulnerablePower(duration=2))

    LoseHPAction(amount=10, target=enemy).execute()
    assert enemy.hp == 40

    helper.game_state.add_action(
        DealDamageAction(
            damage=4,
            target=player,
            source=enemy,
            damage_type=DamageType.PHYSICAL,
        )
    )
    helper.game_state.drive_actions()
    assert enemy.hp == 37


def test_thorns_and_sourceless_hits_are_capped_by_intangible():
    helper, player, enemy = _setup()
    player.add_power(ThornsPower(amount=3))
    player.add_power(StrengthPower(amount=5))
    enemy.add_power(IntangiblePower(duration=1))

    helper.game_state.add_action(
        DealDamageAction(
            damage=10,
            target=enemy,
            source=None,
            damage_type=DamageType.PHYSICAL,
        )
    )
    helper.game_state.drive_actions()
    assert enemy.hp == 49

    enemy.hp = 50
    helper.game_state.add_action(
        DealDamageAction(
            damage=4,
            target=player,
            source=enemy,
            damage_type=DamageType.PHYSICAL,
        )
    )
    helper.game_state.drive_actions()
    assert enemy.hp == 49


def test_whirlwind_uses_strength_and_weak_on_every_hit():
    helper, player, enemy = _setup(energy=1)
    player.add_power(StrengthPower(amount=3))
    player.add_power(WeakPower(duration=2))

    PlayCardBHAction(Whirlwind(), [enemy]).execute()
    helper.game_state.drive_actions()

    assert enemy.hp == 44


def test_playing_a_multi_hit_attack_doubles_every_hit_then_removes_pen_nib():
    helper, player, enemy = _setup(energy=3)
    player.add_power(PenNibPower())

    PlayCardBHAction(TwinStrike(), [enemy]).execute()
    helper.game_state.drive_actions()

    assert enemy.hp == 30
    assert player.get_power("PenNib") is None

    PlayCardBHAction(TwinStrike(), [enemy]).execute()
    helper.game_state.drive_actions()
    assert enemy.hp == 20


def test_playing_a_skill_does_not_remove_pen_nib():
    helper, player, _enemy = _setup(energy=3)
    player.add_power(PenNibPower())

    PlayCardBHAction(Defend(), [player]).execute()
    helper.game_state.drive_actions()

    assert player.get_power("PenNib") is not None


def test_hp_loss_ignores_vulnerable_but_intangible_caps_it():
    _, _player, enemy = _setup()
    enemy.add_power(VulnerablePower(duration=2))
    LoseHPAction(amount=10, target=enemy).execute()
    assert enemy.hp == 40

    enemy.add_power(IntangiblePower(duration=1))
    LoseHPAction(amount=10, target=enemy).execute()
    assert enemy.hp == 39
