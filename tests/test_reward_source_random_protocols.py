"""Regression tests for source-specific reward draws and reservation order."""
from typing import cast
from unittest.mock import patch

import pytest

from actions.combat_status import UsePotionBHAction
from actions.misc import OpenChestAction
from actions.reward import AddEliteRelicAction, AddPotionAction, AddRelicAction
from cards.colorless.doubt import Doubt
from cards.ironclad.strike import Strike
from cards.silent.alchemize import Alchemize
from engine.card_pools import original_id
from engine.game_state import game_state
from player.player_factory import create_player
from potions.global_potions import EntropicBrew, FirePotion
from potions.pool import catalog
from relics.global_relics.boss import BlackStar, CursedKey, TinyHouse
from relics.global_relics.common import Omamori
from relics.global_relics.shop import Cauldron
from relics.global_relics.uncommon import Matryoshka
from rooms.combat import CombatRoom
from rooms.treasure import TreasureRoom
from tests.test_deferred_damage_protocols import play, prepare
from utils.compatible_random import GameRandom
from utils.result_types import GameTerminalState
from utils.types import RarityType, RoomType


@pytest.mark.parametrize("run_seed", [0, 3])
def test_elite_room_reserves_base_before_black_star(run_seed):
    game_state.player.relics = [BlackStar()]
    game_state.current_floor = 5
    rng = game_state.random_streams["relic"]
    rng.seed(run_seed)
    for _ in range(5):
        rng.random_long()
    game_state.relic_pools.remaining.update(
        UNCOMMON=["HornCleat", "Matryoshka"], COMMON=["Anchor"]
    )
    room = CombatRoom(room_type=RoomType.ELITE)
    game_state.current_room = room
    room.init()
    assert room.combat is not None
    with patch.object(room.combat, "start", return_value=GameTerminalState.COMBAT_WIN):
        room.enter()

    rewards = [cast(AddEliteRelicAction, action) for action in game_state.action_queue.queue
               if isinstance(action, AddEliteRelicAction)]
    assert [action.non_campfire for action in rewards] == [False, True]
    for reward in rewards:
        reward.execute()
    expected = ["HornCleat", "Anchor" if run_seed == 0 else "Matryoshka"]
    assert [getattr(relic, "idstr", None) for relic in game_state.player.relics[1:]] == expected
    assert rng.counter == 7


@pytest.mark.parametrize("size", ["small", "medium", "large"])
def test_matryoshka_reserves_extra_before_same_tier_base(size):
    matryoshka = Matryoshka()
    game_state.player.relics = [matryoshka]
    game_state.current_floor = 5
    rng = game_state.random_streams["relic"]
    rng.seed(0)
    for _ in range(5):
        rng.random_long()
    game_state.relic_pools.remaining["UNCOMMON"] = ["HornCleat", "EternalFeather"]
    room = TreasureRoom()
    room.chest_type = size
    room.chest_reward = (0, RarityType.UNCOMMON)
    OpenChestAction(room).execute()
    OpenChestAction(room).execute()
    game_state.drive_actions()

    assert rng.counter == 6
    assert matryoshka.chests_to_spawn == 1
    assert [getattr(relic, "idstr", None) for relic in game_state.player.relics[1:]] == ["HornCleat", "EternalFeather"]


@pytest.mark.parametrize("blocked", [False, True])
def test_cursed_key_draws_from_card_stream_even_when_omamori_blocks(blocked):
    player = game_state.player
    omamori = Omamori()
    player.relics = [CursedKey(), omamori] if blocked else [CursedKey()]
    deck = player.card_manager.get_pile("deck")
    old_count = len(deck)
    card_rng = game_state.random_streams["card"]
    card_rng.seed(0)
    combat_rng = game_state.random_streams["card_random"]
    before = combat_rng.export_state()
    room = TreasureRoom()
    room.chest_type = "large"
    room.chest_reward = (0, RarityType.COMMON)
    OpenChestAction(room).execute()
    game_state.drive_actions()

    assert card_rng.counter == 1
    assert combat_rng.export_state() == before
    assert len(deck) == old_count + int(not blocked)
    if blocked:
        assert omamori.curses_to_negate == 1
    else:
        assert any(original_id(card) == "Shame" for card in deck)


def test_alchemize_uses_limited_potion_draw():
    player, _, _ = prepare("silent")
    rng = game_state.random_streams["potion"]
    rng.seed(3)
    assert play(Alchemize()) is None
    assert player.potions[0]._original_potion_id == "GhostInAJar"
    assert rng.counter == 6


def test_combat_entropic_brew_draws_for_all_slots_and_does_not_replace():
    player, _, _ = prepare("silent")
    brew = EntropicBrew()
    held = [FirePotion(), FirePotion()]
    player.potion_limit = 3
    player.potions.extend([brew, *held])
    rng = game_state.random_streams["potion"]
    rng.seed(3)

    UsePotionBHAction(potion=brew, targets=[player]).execute()
    generated = [cast(AddPotionAction, action).potion for action in game_state.action_queue.queue
                 if isinstance(action, AddPotionAction)]
    assert len(generated) == 3
    assert generated[0]._original_potion_id == "GhostInAJar"
    assert all(potion._original_potion_id != "Fruit Juice" for potion in generated)
    assert game_state.drive_actions() is None
    assert list(player.potions) == [*held, generated[0]]


def test_cauldron_generates_five_uniform_potions_before_receipt():
    game_state.player = create_player("silent")
    game_state.player.potion_limit = 1
    rng = game_state.random_streams["potion"]
    rng.seed(0)
    AddRelicAction(Cauldron()).execute()

    queued = [cast(AddPotionAction, action).potion for action in game_state.action_queue.queue
              if isinstance(action, AddPotionAction)]
    assert [potion._original_potion_id for potion in queued] == [
        "CunningPotion", "CunningPotion", "Block Potion", "Regen Potion", "Block Potion"
    ]
    assert rng.counter == 5


@pytest.mark.parametrize("has_upgrade", [False, True])
def test_tiny_house_draws_from_misc_after_upgrade_shuffle(has_upgrade):
    player = game_state.player = create_player("silent")
    card = Strike() if has_upgrade else Doubt()
    player.card_manager.piles["deck"] = [card]
    misc = game_state.random_streams["misc"]
    misc.seed(3)
    potion = game_state.random_streams["potion"].export_state()
    expected = GameRandom(3)
    expected.random_long()
    ids = catalog()["pools"]["silent"]
    expected_id = ids[expected.random_int(len(ids) - 1)]

    TinyHouse().on_obtain()
    while not player.potions:
        assert not game_state.action_queue.is_empty()
        game_state.action_queue.execute_next()
    assert card.upgrade_level == int(has_upgrade)
    assert player.potions[0]._original_potion_id == expected_id
    assert misc.export_state() == expected.export_state()
    assert game_state.random_streams["potion"].export_state() == potion
