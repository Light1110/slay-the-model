"""Regression contracts for PWR-018/019/020 against the original game rules."""
import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_damage import DealDamageAction, LoseHPAction
from actions.combat_status import ApplyPowerAction
from cards.ironclad.feed import Feed
from cards.silent.corpse_explosion import CorpseExplosion
from enemies.act1.cultist import Cultist
from enemies.act1.fungi_beast import FungiBeast
from enemies.act3.awakened_one import AwakenedOne
from enemies.act3.darkling import Darkling
from engine.messages import CreatureDiedMessage, EnemyHpDepletedMessage, FatalDamageMessage
from powers.definitions.corpse_explosion import CorpseExplosionPower
from powers.definitions.strength import StrengthPower
from powers.definitions.weak import WeakPower
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState
from utils.types import DamageType


def setup_combat(*enemies):
    helper = create_test_helper()
    helper.create_player(hp=200, max_hp=200, energy=30)
    helper.game_state.player.base_draw_count = 0
    helper.start_combat(list(enemies))
    return helper


def capture(gs, monkeypatch):
    messages = []
    original = gs.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(gs, "publish_message", publish)
    return messages


def play_corpse_explosion(helper, target, stacks):
    # The real selection backend chooses the first enemy, which is target.
    assert helper.game_state.current_combat.enemies[0] is target
    for _ in range(stacks):
        card = CorpseExplosion()
        helper.add_card_to_hand(card)
        helper.game_state.add_action(PlayCardAction(card))
        helper.game_state.drive_actions()


def kill(helper, target, kind):
    gs = helper.game_state
    if kind == "poison":
        # Stop after the genuine poison tick to inspect a half-dead transition
        # before that enemy can execute its newly selected rebirth intention.
        target.get_power("Poison").on_turn_start()
    elif kind == "hp_loss":
        gs.add_action(LoseHPAction(amount=target.hp + 50, target=target))
    else:
        gs.add_action(DealDamageAction(target.hp + 50, target, source=gs.player,
                                       damage_type=DamageType.PHYSICAL))
    gs.drive_actions()


@pytest.mark.parametrize("kind", ["attack", "hp_loss", "poison"])
@pytest.mark.parametrize("stacks", [1, 2, 3])
def test_native_corpse_explosion_uses_all_stacks_for_every_kill_path(kind, stacks, monkeypatch):
    target, other = Cultist(), Cultist()
    helper = setup_combat(target, other)
    target._max_hp = 20
    target.hp = 1
    other._max_hp = 200
    other.hp = 200
    messages = capture(helper.game_state, monkeypatch)
    play_corpse_explosion(helper, target, stacks)

    assert target.get_power("Corpse Explosion").amount == stacks
    kill(helper, target, kind)

    assert other.hp == 200 - 20 * stacks
    assert sum(isinstance(m, EnemyHpDepletedMessage) and m.creature is target for m in messages) == 1
    assert sum(isinstance(m, CreatureDiedMessage) and m.creature is target for m in messages) == 1
    hits = [m for m in messages if getattr(m, "target", None) is other and type(m).__name__ == "DamageDealtMessage"]
    assert len(hits) == 1 and hits[0].damage_type == DamageType.THORNS


@pytest.mark.parametrize("kind", ["attack", "hp_loss", "poison"])
@pytest.mark.parametrize("enemy_class", [AwakenedOne, Darkling])
@pytest.mark.parametrize("stacks", [1, 2])
def test_half_dead_collapse_triggers_explosion_before_power_cleanup(kind, enemy_class, stacks, monkeypatch):
    target = enemy_class()
    other = Darkling() if enemy_class is Darkling else Cultist()
    helper = setup_combat(target, other)
    target._max_hp = 20
    target.hp = 1
    other._max_hp = 200
    other.hp = 200
    target.add_power(StrengthPower(amount=3, owner=target))
    messages = capture(helper.game_state, monkeypatch)
    play_corpse_explosion(helper, target, stacks)
    kill(helper, target, kind)

    assert target.hp == 0 and target.half_dead and not target.is_dead()
    assert other.hp == 200 - 20 * stacks
    assert target.get_power("Poison") is None
    assert target.get_power("Corpse Explosion") is None
    if enemy_class is Darkling:
        assert target.powers == []
        assert target.current_intention.name == "Regrowing..."
    else:
        assert target.get_power("Curiosity") is None
        assert target.get_power("Strength").amount == 3
        assert target.current_intention.name == "Rebirth"
    collapse = [m for m in messages if isinstance(m, EnemyHpDepletedMessage) and m.creature is target]
    assert len(collapse) == 1 and collapse[0].half_dead
    assert not any(isinstance(m, CreatureDiedMessage) and m.creature is target for m in messages)
    assert not any(isinstance(m, FatalDamageMessage) and m.target is target for m in messages)
    combat = helper.game_state.current_combat
    assert combat is not None
    assert combat._check_combat_end() is None

    kill(helper, target, "hp_loss")
    kill(helper, target, "attack")
    assert other.hp == 200 - 20 * stacks
    assert sum(isinstance(m, EnemyHpDepletedMessage) and m.creature is target for m in messages) == 1


@pytest.mark.parametrize("kind", ["attack", "hp_loss", "poison"])
def test_fungi_death_reaction_runs_once_for_every_kill_path(kind, monkeypatch):
    target, other = FungiBeast(), Cultist()
    helper = setup_combat(target, other)
    target.hp = 1
    messages = capture(helper.game_state, monkeypatch)
    if kind == "poison":
        from powers.definitions.poison import PoisonPower
        target.add_power(PoisonPower(amount=3, duration=3, owner=target))
    kill(helper, target, kind)
    kill(helper, target, "hp_loss")
    vulnerable = helper.game_state.player.get_power("Vulnerable")
    assert vulnerable is not None
    assert vulnerable.amount == 2
    assert sum(isinstance(m, CreatureDiedMessage) and m.creature is target for m in messages) == 1


@pytest.mark.parametrize("enemy_class", [AwakenedOne, Darkling])
def test_revival_allows_a_new_collapse_and_new_explosion(enemy_class, monkeypatch):
    target = enemy_class()
    other = Darkling() if enemy_class is Darkling else Cultist()
    helper = setup_combat(target, other)
    target._max_hp = 20
    target.hp = 1
    other._max_hp = 200
    other.hp = 200
    messages = capture(helper.game_state, monkeypatch)
    play_corpse_explosion(helper, target, 1)
    kill(helper, target, "attack")
    target.intentions["Reincarnate" if enemy_class is Darkling else "Rebirth"].execute()
    assert target.hp > 0 and not target.half_dead
    play_corpse_explosion(helper, target, 2)
    kill(helper, target, "hp_loss")

    assert other.hp == 140
    assert sum(isinstance(m, EnemyHpDepletedMessage) and m.creature is target for m in messages) == 2
    deaths = [m for m in messages if isinstance(m, CreatureDiedMessage) and m.creature is target]
    assert len(deaths) == (0 if enemy_class is Darkling else 1)


def test_link_survives_power_cleanup_and_reincarnation():
    first, second = Darkling(), Darkling()
    helper = setup_combat(first, second)
    kill(helper, first, "hp_loss")
    assert first.get_power("Life Link") is None
    first.intentions["Reincarnate"].execute()
    kill(helper, second, "hp_loss")
    # The revived sibling has no Life Link power, but is still a Darkling.
    assert second.half_dead and not second.is_dead()
    combat = helper.game_state.current_combat
    assert combat is not None
    assert combat._check_combat_end() is None


def test_last_darkling_collapse_finalizes_group_without_repeating_reactions(monkeypatch):
    first, second = Darkling(), Darkling()
    helper = setup_combat(first, second)
    messages = capture(helper.game_state, monkeypatch)
    kill(helper, first, "hp_loss")
    kill(helper, second, "hp_loss")
    assert first.is_dead() and second.is_dead()
    assert not first.half_dead and not second.half_dead
    for enemy in [first, second]:
        assert sum(isinstance(m, EnemyHpDepletedMessage) and m.creature is enemy for m in messages) == 1
        assert sum(isinstance(m, CreatureDiedMessage) and m.creature is enemy for m in messages) == 1
    assert sum(isinstance(m, FatalDamageMessage) for m in messages) == 1
    combat = helper.game_state.current_combat
    assert combat is not None
    assert combat._check_combat_end() == GameTerminalState.COMBAT_WIN


def test_chained_explosions_do_not_repeat_or_trigger_a_living_owners_power(monkeypatch):
    enemies = [Cultist() for _ in range(4)]
    helper = setup_combat(*enemies)
    for enemy in enemies[:3]:
        enemy._max_hp = 10
        enemy.hp = 1
        helper.game_state.add_action(ApplyPowerAction(CorpseExplosionPower(amount=2), enemy))
    anchor = enemies[-1]
    anchor._max_hp = 300
    anchor.hp = 300
    helper.game_state.add_action(ApplyPowerAction(CorpseExplosionPower(), anchor))
    helper.game_state.drive_actions()
    messages = capture(helper.game_state, monkeypatch)
    kill(helper, enemies[0], "attack")
    assert anchor.hp == 240
    for enemy in enemies[:3]:
        assert sum(isinstance(m, EnemyHpDepletedMessage) and m.creature is enemy for m in messages) == 1
        assert sum(isinstance(m, CreatureDiedMessage) and m.creature is enemy for m in messages) == 1
    combat = helper.game_state.current_combat
    assert combat is not None
    assert combat._check_combat_end() is None


def test_poison_death_does_not_grant_a_hand_cards_fatal_reward():
    target, other = Cultist(), Cultist()
    helper = setup_combat(target, other)
    helper.add_card_to_hand(Feed())
    original_max_hp = helper.game_state.player.max_hp
    helper.game_state.add_action(LoseHPAction(target.hp, target=target))
    helper.game_state.drive_actions()
    assert helper.game_state.player.max_hp == original_max_hp


def test_blocked_zero_and_nonlethal_damage_do_not_trigger_collapse(monkeypatch):
    target, other = Cultist(), Cultist()
    helper = setup_combat(target, other)
    target._max_hp = 20
    target.hp = 20
    target.block = 5
    target.add_power(CorpseExplosionPower(owner=target))
    messages = capture(helper.game_state, monkeypatch)
    for damage in [0, 5, 1]:
        helper.game_state.add_action(DealDamageAction(damage, target))
    helper.game_state.drive_actions()
    assert target.hp == 19
    assert not any(isinstance(m, EnemyHpDepletedMessage) for m in messages)


def test_previously_saved_enemy_without_lifecycle_fields_can_still_die(monkeypatch):
    import pickle

    target, other = Cultist(), Cultist()
    # Older pickle payloads have no fields introduced by this fix.
    del target._hp_depletion_handled
    del target._death_notified
    target = pickle.loads(pickle.dumps(target))
    helper = setup_combat(target, other)
    messages = capture(helper.game_state, monkeypatch)
    helper.game_state.add_action(LoseHPAction(target.hp, target=target))
    helper.game_state.drive_actions()
    assert target.is_dead()
    assert sum(isinstance(m, CreatureDiedMessage) and m.creature is target for m in messages) == 1
