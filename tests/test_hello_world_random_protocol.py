import pickle

import pytest

from cards.defect.hello_world import HelloWorld
from cards.ironclad.defend import Defend
from engine.card_pools import current_pools, original_id
from engine.game_state import game_state
from engine.random_streams import StreamRandom
from powers.base import StackType
from powers.definitions.hello_world import HelloWorldPower
from tests.test_deferred_damage_protocols import play, prepare
from utils.types import RarityType


@pytest.mark.parametrize("copies", [1, 2, 4])
def test_hello_world_selects_each_stack_before_adding_cards_and_drawing(copies):
    player, _, combat = prepare(role="defect")
    for _ in range(copies):
        assert play(HelloWorld()) is None
    power, = [power for power in player.powers if isinstance(power, HelloWorldPower)]
    assert power.amount == copies

    pools = current_pools()
    pools.current[("defect", "COMMON")].pop(0)
    candidates = pools.candidates(["defect"], [RarityType.COMMON], pool_kind="current")
    reference = StreamRandom(0)
    expected = [reference.choice(candidates) for _ in range(copies)]
    rng = game_state.random_streams["card_random"]
    rng.seed(0)
    drawn = Defend()
    player.base_draw_count = 1
    player.card_manager.piles["draw_pile"] = [drawn]
    combat.combat_state.combat_turn = 1

    combat._start_player_turn()
    assert rng.export_state() == reference.export_state()
    assert player.card_manager.piles["hand"] == []
    assert game_state.drive_actions() is None

    hand = player.card_manager.piles["hand"]
    assert [original_id(card) for card in hand[:-1]] == expected
    assert hand[-1] is drawn
    assert rng.export_state() == reference.export_state()


def test_deserialized_legacy_hello_world_contributes_one_stack():
    player, _, _ = prepare(role="defect")
    legacy = HelloWorldPower(amount=0)
    legacy.stack_type = StackType.PRESENCE
    restored = pickle.loads(pickle.dumps(legacy))
    player.add_power(restored)

    assert play(HelloWorld()) is None
    assert restored.amount == 2
    assert restored.stack_type is StackType.INTENSITY
