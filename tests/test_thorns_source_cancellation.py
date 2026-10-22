"""PWR-021/036: resolve thorns between hits and cancel inactive sources."""
import pytest

from actions.combat_cards import PlayCardAction
from actions.combat_damage import DealDamageAction
from cards.silent.riddle_with_holes import RiddleWithHoles
from enemies.act1.cultist import Cultist
from enemies.act2.snake_plant import SnakePlant
from enemies.act3.awakened_one import AwakenedOne
from engine.messages import BlockGainedMessage, DamageDealtMessage
from potions.global_potions import FairyInABottle
from powers.definitions.buffer import BufferPower
from powers.definitions.malleable import MalleablePower
from powers.definitions.thorns import ThornsPower
from relics.global_relics.rare import LizardTail
from tests.test_combat_utils import create_test_helper
from utils.result_types import GameTerminalState
from utils.types import DamageType


def setup_combat(*enemies, hp=100):
    helper = create_test_helper()
    player = helper.create_player(max_hp=100, hp=hp, energy=30)
    player.base_draw_count = 0
    helper.start_combat(list(enemies))
    return helper, player


def observe(gs, monkeypatch):
    messages = []
    original = gs.publish_message

    def publish(message, *args, **kwargs):
        messages.append(message)
        return original(message, *args, **kwargs)

    monkeypatch.setattr(gs, "publish_message", publish)
    return messages


def damage_messages(messages):
    return [message for message in messages if isinstance(message, DamageDealtMessage)]


def play_riddle(helper, upgraded=False):
    card = RiddleWithHoles()
    if upgraded:
        card.upgrade()
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    return helper.game_state.drive_actions()


@pytest.mark.parametrize("enemy_class,intent,expected_hp", [
    (SnakePlant, "chomp_chomp", 93),
    (AwakenedOne, "Soul Strike", 94),
])
def test_native_multihit_stops_when_thorns_kill_or_half_kill_source(
        enemy_class, intent, expected_hp, monkeypatch):
    source, anchor = enemy_class(), Cultist()
    helper, player = setup_combat(source, anchor)
    source.hp = 3
    player.add_power(ThornsPower(amount=3, owner=player))
    messages = observe(helper.game_state, monkeypatch)

    source.intentions[intent].execute()
    assert helper.game_state.drive_actions() is None

    assert player.hp == expected_hp
    assert source.hp == 0
    assert source.half_dead == (enemy_class is AwakenedOne)
    hits = damage_messages(messages)
    assert len(hits) == 2
    assert hits[0].source is source and hits[0].target is player
    assert hits[1].source is player and hits[1].target is source
    assert hits[1].damage_type == DamageType.THORNS


@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("save,expected_hp", [("none", 0), ("fairy", 18), ("tail", 38)])
def test_real_player_multihit_stops_on_death_but_continues_after_save(
        upgraded, save, expected_hp, monkeypatch):
    enemy = Cultist()
    helper, player = setup_combat(enemy, hp=3)
    enemy._max_hp = 100
    enemy.hp = 100
    enemy.add_power(ThornsPower(amount=3, owner=enemy))
    if save == "fairy":
        player.potions.append(FairyInABottle())
    elif save == "tail":
        player.relics.append(LizardTail())
    messages = observe(helper.game_state, monkeypatch)

    result = play_riddle(helper, upgraded)

    assert result == (GameTerminalState.GAME_LOSE if save == "none" else None)
    assert player.hp == expected_hp
    hit_count = 1 if save == "none" else 5
    assert enemy.hp == 100 - (4 if upgraded else 3) * hit_count
    hits = damage_messages(messages)
    assert len(hits) == 2 * hit_count
    assert [hit.target for hit in hits] == [enemy, player] * hit_count
    assert [hit.damage_type for hit in hits] == [DamageType.PHYSICAL, DamageType.THORNS] * hit_count


@pytest.mark.parametrize("direction", ["enemy", "player"])
def test_nonlethal_thorns_alternate_with_original_hits(direction, monkeypatch):
    enemy = SnakePlant() if direction == "enemy" else Cultist()
    helper, player = setup_combat(enemy)
    enemy._max_hp = 100
    enemy.hp = 100
    defender = player if direction == "enemy" else enemy
    attacker = enemy if direction == "enemy" else player
    defender.add_power(ThornsPower(amount=3, owner=defender))
    messages = observe(helper.game_state, monkeypatch)

    if direction == "enemy":
        enemy.intentions["chomp_chomp"].execute()
        assert helper.game_state.drive_actions() is None
    else:
        assert play_riddle(helper) is None

    count = 3 if direction == "enemy" else 5
    hits = damage_messages(messages)
    assert [hit.target for hit in hits] == [defender, attacker] * count
    assert [hit.damage_type for hit in hits] == [DamageType.PHYSICAL, DamageType.THORNS] * count


def prepared_source(state):
    source = AwakenedOne() if state == "half_dead" else Cultist()
    helper, player = setup_combat(source, Cultist())
    if state != "alive":
        source.hp = 0
    assert source.half_dead == (state == "half_dead")
    return helper, player, source


@pytest.mark.parametrize("state", ["alive", "dead", "half_dead"])
@pytest.mark.parametrize("damage_type", [DamageType.PHYSICAL, DamageType.THORNS])
def test_source_state_contract_preserves_thorns_exception(state, damage_type, monkeypatch):
    helper, player, source = prepared_source(state)
    messages = observe(helper.game_state, monkeypatch)
    helper.game_state.add_action(DealDamageAction(7, player, source=source, damage_type=damage_type))

    assert helper.game_state.drive_actions() is None

    allowed = state == "alive" or damage_type == DamageType.THORNS
    assert player.hp == (93 if allowed else 100)
    hits = damage_messages(messages)
    assert len(hits) == int(allowed)


@pytest.mark.parametrize("state", ["dead", "half_dead"])
def test_cancelled_source_does_not_spend_block_or_buffer(state, monkeypatch):
    helper, player, source = prepared_source(state)
    player.block = 3
    buffer = BufferPower(amount=1, owner=player)
    player.add_power(buffer)
    messages = observe(helper.game_state, monkeypatch)
    helper.game_state.add_action(DealDamageAction(7, player, source=source, damage_type=DamageType.PHYSICAL))

    assert helper.game_state.drive_actions() is None

    assert player.hp == 100 and player.block == 3
    assert player.get_power("Buffer") is buffer and buffer.amount == 1
    assert damage_messages(messages) == []


@pytest.mark.parametrize("target_kind", ["player", "enemy"])
def test_thorns_accepts_no_source(target_kind, monkeypatch):
    enemy = Cultist()
    helper, player = setup_combat(enemy)
    enemy._max_hp = 100
    enemy.hp = 100
    target = player if target_kind == "player" else enemy
    messages = observe(helper.game_state, monkeypatch)
    helper.game_state.add_action(DealDamageAction(7, target, source=None, damage_type=DamageType.THORNS))

    assert helper.game_state.drive_actions() is None

    assert target.hp == 93
    assert len(damage_messages(messages)) == 1


def test_malleable_keeps_its_original_tail_queue_contract(monkeypatch):
    enemy = Cultist()
    helper, player = setup_combat(enemy)
    enemy._max_hp = 100
    enemy.hp = 100
    enemy.add_power(MalleablePower(amount=3, owner=enemy))
    messages = observe(helper.game_state, monkeypatch)

    assert play_riddle(helper) is None

    assert enemy.hp == 85 and enemy.block == 25
    relevant = [type(message) for message in messages
                if isinstance(message, (DamageDealtMessage, BlockGainedMessage))]
    assert relevant == [DamageDealtMessage] * 5 + [BlockGainedMessage] * 5


@pytest.mark.parametrize("state", ["alive", "dead", "half_dead"])
def test_cancelled_outer_attack_does_not_steal_gold(state, monkeypatch):
    from actions.combat_cards import AttackAction
    from engine.messages import AttackPerformedMessage
    from powers.definitions.thievery import ThieveryPower

    helper, player, source = prepared_source(state)
    theft = ThieveryPower(amount=15, owner=source)
    source.add_power(theft)
    initial_gold = player.gold
    messages = observe(helper.game_state, monkeypatch)
    helper.game_state.add_action(AttackAction(7, player, source=source))
    assert helper.game_state.drive_actions() is None
    allowed = state == "alive"
    assert player.gold == initial_gold - (15 if allowed else 0)
    assert theft.stolen_gold == (15 if allowed else 0)
    assert player.hp == (93 if allowed else 100)
    assert sum(isinstance(m, AttackPerformedMessage) for m in messages) == int(allowed)


@pytest.mark.parametrize("kind,damage", [("Cleave", 8), ("Whirlwind", 5), ("Blizzard", 6)])
def test_native_aoe_keeps_remaining_targets_after_source_dies(kind, damage):
    from cards.ironclad.cleave import Cleave
    from cards.ironclad.whirlwind import Whirlwind
    from cards.defect.blizzard import Blizzard

    first, second = Cultist(), Cultist()
    helper, player = setup_combat(first, second, hp=3)
    for enemy in [first, second]:
        enemy._max_hp = 100
        enemy.hp = 100
    first.add_power(ThornsPower(amount=3, owner=first))
    player.energy = 1
    combat = helper.game_state.current_combat
    assert combat is not None
    combat.combat_state.orb_history["Frost"] = 3
    card = {"Cleave": Cleave, "Whirlwind": Whirlwind, "Blizzard": Blizzard}[kind]()
    helper.add_card_to_hand(card)
    helper.game_state.add_action(PlayCardAction(card))
    assert helper.game_state.drive_actions() == GameTerminalState.GAME_LOSE
    assert player.hp == 0
    # DamageAllEnemiesAction has no ordinary single-target source guard.
    # This checks remaining damage, not full AoE reaction atomicity.
    assert [first.hp, second.hp] == [100 - damage, 100 - damage]


@pytest.mark.parametrize("source_kind", ["none", "dead"])
def test_magical_shared_effects_are_not_given_a_blanket_source_guard(source_kind):
    helper, player, source = prepared_source("dead")
    helper.game_state.add_action(DealDamageAction(
        7, player, source=None if source_kind == "none" else source,
        damage_type=DamageType.MAGICAL))
    assert helper.game_state.drive_actions() is None
    assert player.hp == 93


@pytest.mark.parametrize("source_class", [Cultist, AwakenedOne])
def test_queued_damage_rechecks_source_after_real_hp_depletion(source_class, monkeypatch):
    from actions.combat_damage import LoseHPAction

    source = source_class()
    helper, player = setup_combat(source, Cultist())
    source.hp = 1
    player.block = 3
    buffer = BufferPower(amount=1, owner=player)
    player.add_power(buffer)
    messages = observe(helper.game_state, monkeypatch)
    helper.game_state.add_action(DealDamageAction(7, player, source=source, damage_type=DamageType.PHYSICAL))
    helper.game_state.add_action(LoseHPAction(1, target=source), to_front=True)
    assert helper.game_state.drive_actions() is None
    assert source.hp == 0
    assert player.hp == 100 and player.block == 3 and buffer.amount == 1
    assert damage_messages(messages) == []


@pytest.mark.parametrize("kind", ["attack", "damage"])
@pytest.mark.parametrize("aoe", [False, True])
def test_old_pickled_actions_without_source_policy_remain_usable(kind, aoe):
    import pickle
    from actions.combat_cards import AttackAction
    from cards.ironclad.cleave import Cleave

    enemy = Cultist()
    helper, player = setup_combat(enemy)
    enemy._max_hp = 100
    enemy.hp = 100
    if aoe:
        player.hp = 0
        source, target, card = player, enemy, Cleave()
    else:
        enemy.hp = 0
        source, target, card = enemy, player, None
    action_type = AttackAction if kind == "attack" else DealDamageAction
    action = action_type(8, target, source=source, card=card, damage_type=DamageType.PHYSICAL)
    del action.cancel_on_source_death
    restored = pickle.loads(pickle.dumps(action))
    helper.game_state.add_action(restored)
    assert helper.game_state.drive_actions() is None
    assert restored.target.hp == (92 if aoe else 100)
