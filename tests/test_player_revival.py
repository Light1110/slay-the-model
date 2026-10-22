"""PWR-013: resolve automatic player saves before death and the next hit."""
import pytest

from actions.combat_damage import DealDamageAction, LoseHPAction
from enemies.act2.snake_plant import SnakePlant
from engine.messages import CreatureDiedMessage, FatalDamageMessage, HealedMessage
from potions.global_potions import FairyInABottle, FirePotion
from relics.character.ironclad import MagicFlower
from relics.global_relics.boss import SacredBark
from relics.global_relics.event import MarkOfBloom
from relics.global_relics.rare import LizardTail
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState
from utils.types import DamageType


def setup_combat(max_hp=100, hp=10):
    helper = create_test_helper()
    player = helper.create_player(max_hp=max_hp, hp=hp)
    player.base_draw_count = 0
    enemy = SnakePlant()
    helper.start_combat([enemy])
    return helper, player, enemy


def observe(gs, monkeypatch):
    messages = []
    original = gs.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(gs, "publish_message", publish)
    return messages


def hurt(helper, enemy, kind, amount):
    player = helper.game_state.player
    action = (LoseHPAction(amount=amount, target=player, source=enemy)
              if kind == "hp_loss" else
              DealDamageAction(amount, player, source=enemy,
                               damage_type=DamageType.PHYSICAL))
    helper.game_state.add_action(action)
    return helper.game_state.drive_actions()


def deaths(messages, player):
    fatal = [m for m in messages if isinstance(m, FatalDamageMessage) and m.target is player]
    died = [m for m in messages if isinstance(m, CreatureDiedMessage) and m.creature is player]
    return len(fatal), len(died)


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
@pytest.mark.parametrize("amount", [10, 150])
@pytest.mark.parametrize("save,expected", [("tail", 50), ("fairy", 30), ("bark", 60)])
def test_lethal_damage_automatically_consumes_one_save(kind, amount, save, expected, monkeypatch):
    helper, player, enemy = setup_combat()
    tail = LizardTail()
    fairy = FairyInABottle()
    if save == "tail":
        player.relics.append(tail)
    else:
        player.potions.append(fairy)
        if save == "bark":
            player.relics.append(SacredBark())
    messages = observe(helper.game_state, monkeypatch)

    result = hurt(helper, enemy, kind, amount)

    assert result is None
    assert player.hp == expected
    assert deaths(messages, player) == (0, 0)
    heals = [m for m in messages if isinstance(m, HealedMessage) and m.target is player]
    assert len(heals) == 1
    assert (heals[0].previous_hp, heals[0].new_hp, heals[0].amount) == (0, expected, expected)
    if save == "tail":
        assert not tail.can_revive
    else:
        assert fairy not in player.potions
    combat = helper.game_state.current_combat
    assert combat is not None
    assert combat._check_combat_end() is None


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
@pytest.mark.parametrize("save", ["tail", "fairy", "bark"])
@pytest.mark.parametrize("max_hp", [1, 101])
def test_percentage_saves_floor_and_have_a_one_hp_minimum(kind, save, max_hp):
    helper, player, enemy = setup_combat(max_hp=max_hp, hp=1)
    if save == "tail":
        player.relics.append(LizardTail())
        expected = max(1, max_hp // 2)
    else:
        player.potions.append(FairyInABottle())
        if save == "bark":
            player.relics.append(SacredBark())
        expected = max(1, max_hp * (60 if save == "bark" else 30) // 100)

    assert hurt(helper, enemy, kind, 1000) is None
    assert player.hp == expected


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
@pytest.mark.parametrize("save,expected", [("tail", 75), ("fairy", 45)])
def test_saving_uses_combat_healing_modifiers(kind, save, expected):
    helper, player, enemy = setup_combat()
    player.relics.append(MagicFlower())
    if save == "tail":
        player.relics.append(LizardTail())
    else:
        player.potions.append(FairyInABottle())

    assert hurt(helper, enemy, kind, 100) is None
    assert player.hp == expected


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
def test_fairies_take_slot_order_priority_over_tail(kind, monkeypatch):
    helper, player, enemy = setup_combat()
    tail = LizardTail()
    first, second, other = FairyInABottle(), FairyInABottle(), FirePotion()
    player.relics.append(tail)
    player.potions.extend([other, first, second])
    messages = observe(helper.game_state, monkeypatch)

    assert hurt(helper, enemy, kind, 100) is None
    assert player.hp == 30 and list(player.potions) == [other, second]
    assert tail.can_revive
    assert hurt(helper, enemy, kind, 100) is None
    assert player.hp == 30 and list(player.potions) == [other]
    assert tail.can_revive
    assert hurt(helper, enemy, kind, 100) is None
    assert player.hp == 50 and list(player.potions) == [other]
    assert not tail.can_revive
    assert deaths(messages, player) == (0, 0)
    assert hurt(helper, enemy, kind, 100) == GameTerminalState.GAME_LOSE
    assert deaths(messages, player) == (1, 1)


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
@pytest.mark.parametrize("save", ["tail", "fairy", "both"])
def test_mark_of_bloom_prevents_saving_without_spending_items(kind, save, monkeypatch):
    helper, player, enemy = setup_combat()
    tail, fairy = LizardTail(), FairyInABottle()
    player.relics.append(MarkOfBloom())
    if save in {"tail", "both"}:
        player.relics.append(tail)
    if save in {"fairy", "both"}:
        player.potions.append(fairy)
    messages = observe(helper.game_state, monkeypatch)

    assert hurt(helper, enemy, kind, 10) == GameTerminalState.GAME_LOSE
    assert player.hp == 0 and tail.can_revive
    if save in {"fairy", "both"}:
        assert fairy in player.potions
    assert not any(isinstance(m, HealedMessage) for m in messages)
    assert deaths(messages, player) == (1, 1)


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
@pytest.mark.parametrize("used_tail", [False, True])
def test_no_available_save_enters_real_death(kind, used_tail, monkeypatch):
    helper, player, enemy = setup_combat()
    if used_tail:
        tail = LizardTail()
        tail.can_revive = False
        player.relics.append(tail)
    messages = observe(helper.game_state, monkeypatch)

    assert hurt(helper, enemy, kind, 10) == GameTerminalState.GAME_LOSE
    assert player.hp == 0
    assert deaths(messages, player) == (1, 1)
    # An already dead target must not emit a second fatal/death pair.
    assert hurt(helper, enemy, "hp_loss", 10) is None
    assert deaths(messages, player) == (1, 1)


@pytest.mark.parametrize("kind", ["attack", "hp_loss"])
def test_nonlethal_damage_does_not_spend_save(kind, monkeypatch):
    helper, player, enemy = setup_combat()
    tail, fairy = LizardTail(), FairyInABottle()
    player.relics.append(tail)
    player.potions.append(fairy)
    messages = observe(helper.game_state, monkeypatch)

    assert hurt(helper, enemy, kind, 9) is None
    assert player.hp == 1 and tail.can_revive and fairy in player.potions
    assert deaths(messages, player) == (0, 0)
    assert not any(isinstance(m, HealedMessage) for m in messages)


@pytest.mark.parametrize("resources,max_hp,expected_hp,expected_heals", [
    ("fairy", 100, 16, [30]),
    ("fairy_tail", 20, 3, [6, 10]),
    ("two_fairies", 20, 0, [6, 6]),
])
def test_native_multihit_continues_after_save_and_can_kill_again(
        resources, max_hp, expected_hp, expected_heals, monkeypatch):
    helper, player, enemy = setup_combat(max_hp=max_hp, hp=3)
    player.potions.append(FairyInABottle())
    if resources == "two_fairies":
        player.potions.append(FairyInABottle())
    if resources == "fairy_tail":
        player.relics.append(LizardTail())
    messages = observe(helper.game_state, monkeypatch)

    # The original enemy intent queues all three 7-damage attacks naturally.
    enemy.intentions["chomp_chomp"].execute()
    result = helper.game_state.drive_actions()

    assert player.hp == expected_hp
    assert result == (GameTerminalState.GAME_LOSE if expected_hp == 0 else None)
    assert [m.amount for m in messages if isinstance(m, HealedMessage)] == expected_heals
    assert player.potions == []
    assert deaths(messages, player) == ((1, 1) if expected_hp == 0 else (0, 0))


def test_fairy_cannot_be_used_through_active_potion_action():
    from actions.combat_status import UsePotionAction

    helper, player, _ = setup_combat()
    fairy = FairyInABottle()
    player.potions.append(fairy)
    helper.game_state.add_action(UsePotionAction(fairy, target=player))
    assert helper.game_state.drive_actions() is None
    assert player.hp == 10 and fairy in player.potions
    assert not fairy.can_be_used_actively


@pytest.mark.parametrize("damage_type", [DamageType.MAGICAL, DamageType.THORNS])
def test_non_attack_damage_also_uses_player_save(damage_type):
    helper, player, enemy = setup_combat()
    player.potions.append(FairyInABottle())
    helper.game_state.add_action(DealDamageAction(10, player, source=enemy, damage_type=damage_type))
    assert helper.game_state.drive_actions() is None
    assert player.hp == 30 and player.potions == []


def test_plain_creature_keeps_existing_fatal_damage_notifications(monkeypatch):
    from entities.creature import Creature

    helper, _, enemy = setup_combat()
    target = Creature(max_hp=10)
    messages = observe(helper.game_state, monkeypatch)
    helper.game_state.add_action(DealDamageAction(10, target, source=enemy))
    assert helper.game_state.drive_actions() is None
    assert target.hp == 0 and deaths(messages, target) == (1, 1)


@pytest.mark.parametrize("save,expected", [("tail", 50), ("fairy", 30)])
def test_skull_paid_exit_can_save_without_leaving_pending_death(save, expected, monkeypatch):
    from events.knowing_skull import KnowingSkull

    helper = create_test_helper()
    player = helper.create_player(max_hp=100, hp=1)
    if save == "tail":
        player.relics.append(LizardTail())
    else:
        player.potions.append(FairyInABottle())
    # Supply the ordinary Leave selection; the event, cost and save execute as-is.
    monkeypatch.setattr(helper.game_state, "_resolve_debug_selection", lambda request: [3])
    messages = observe(helper.game_state, monkeypatch)
    event = KnowingSkull()
    event.trigger()
    assert helper.game_state.drive_actions() is None
    assert player.hp == expected and event.event_ended
    assert helper.game_state.action_queue.is_empty()
    assert helper.game_state.pending_input_request is None
    assert deaths(messages, player) == (0, 0)
