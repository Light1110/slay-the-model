"""Verify generation is sampled before the queued hand changes."""
import pytest

from cards.colorless.jack_of_all_trades import JackOfAllTrades
from cards.ironclad.defend import Defend
from engine.card_pools import current_pools, original_id
from engine.game_state import game_state
from engine.messages import PlayerTurnStartedMessage
from engine.random_streams import StreamRandom
from powers.definitions.creative_ai import CreativeAIPower
from powers.definitions.magnetism import MagnetismPower
from tests.test_deferred_damage_protocols import prepare
from utils.types import CardType


def assert_generation_result(expected_ids, reference, initial_hand):
    player = game_state.player
    hand = player.card_manager.piles["hand"]
    discard = player.card_manager.piles["discard_pile"]
    rng = game_state.random_streams["card_random"]
    assert hand == initial_hand
    assert not discard
    assert rng.export_state() == reference.export_state()

    # A second consumer can read the next value before generation settles.
    assert rng.random_int(1000) == reference.random_int(1000)
    assert game_state.drive_actions() is None

    assert hand[:len(initial_hand)] == initial_hand
    assert len(hand) == min(10, len(initial_hand) + len(expected_ids))
    generated = hand[len(initial_hand):] + discard
    assert [original_id(card) for card in generated] == expected_ids
    assert len({id(card) for card in generated}) == len(generated)
    assert rng.export_state() == reference.export_state()


@pytest.mark.parametrize("power_class", [CreativeAIPower, MagnetismPower])
@pytest.mark.parametrize("amount", [1, 2])
@pytest.mark.parametrize("hand_size", [0, 9, 10])
def test_turn_start_powers_sample_every_stack_before_add_actions(power_class, amount, hand_size):
    player, enemies, _ = prepare("defect")
    initial_hand = [Defend() for _ in range(hand_size)]
    player.card_manager.piles["hand"] = initial_hand.copy()
    for _ in range(amount):
        player.add_power(power_class(amount=1, owner=player))

    rng = game_state.random_streams["card_random"]
    rng.seed(523)
    reference = StreamRandom(523)
    if power_class is CreativeAIPower:
        pool = current_pools().candidates(["defect"], card_types=[CardType.POWER], pool_kind="combat")
        assert "Self Repair" not in pool
    else:
        pool = current_pools().candidates(["colorless"], pool_kind="combat")
    expected = [pool[reference.random_int(len(pool) - 1)] for _ in range(amount)]

    game_state.publish_message(PlayerTurnStartedMessage(owner=player, enemies=list(enemies)))

    assert_generation_result(expected, reference, initial_hand)


@pytest.mark.parametrize("upgraded", [False, True])
@pytest.mark.parametrize("hand_size", [0, 9, 10])
def test_jack_of_all_trades_samples_before_add_actions(upgraded, hand_size):
    player, enemies, _ = prepare()
    initial_hand = [Defend() for _ in range(hand_size)]
    player.card_manager.piles["hand"] = initial_hand.copy()
    card = JackOfAllTrades()
    if upgraded:
        card.upgrade()
    rng = game_state.random_streams["card_random"]
    rng.seed(1)
    reference = StreamRandom(1)
    pool = current_pools().candidates(["colorless"], pool_kind="combat")
    expected = [pool[reference.random_int(len(pool) - 1)] for _ in range(2 if upgraded else 1)]

    card.on_play(list(enemies))

    assert_generation_result(expected, reference, initial_hand)


@pytest.mark.parametrize("ended", [False, True])
def test_magnetism_skips_sampling_after_combat(ended):
    player, enemies, combat = prepare()
    player.add_power(MagnetismPower(amount=2, owner=player))
    combat.combat_ended = ended
    if not ended:
        enemies.clear()
    rng = game_state.random_streams["card_random"]
    before = rng.export_state()

    game_state.publish_message(PlayerTurnStartedMessage(owner=player, enemies=list(enemies)))

    assert rng.export_state() == before
    assert game_state.action_queue.is_empty()
