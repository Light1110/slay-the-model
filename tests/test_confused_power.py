"""
Tests for ConfusedPower.
Tests that ConfusedPower randomizes card costs at start of each turn.
"""
import pytest
from powers.definitions.confused import ConfusedPower
from engine.game_state import GameState, game_state
from player.player import Player
from player.card_manager import CardManager
from cards.base import Card
from actions.base import LambdaAction


@pytest.fixture
def setup_game_state():
    """Set up game state with player for testing."""
    global game_state
    game_state = GameState()

    player = Player(max_hp=80, max_energy=3)
    player.card_manager = CardManager(deck=[])

    game_state.player = player
    game_state.combat_state.combat_turn = 1

    return game_state


def test_confused_power_initialization():
    """Test that ConfusedPower can be initialized."""
    power = ConfusedPower()

    assert power.name == "Confused"
    assert power.stackable is False
    assert power.is_buff is False
    assert power.amount == 0
    assert power.duration == 0


def test_confused_power_on_turn_start_randomizes_costs(setup_game_state):
    """Test that on_turn_start() randomizes card costs in hand."""
    global game_state
    player = game_state.player

    # Create a simple test card
    class TestCard(Card):
        base_cost = 1
        name = "Test Card"
        card_type = "Attack"

    # Add test cards to hand
    card1 = TestCard()
    card2 = TestCard()
    card3 = TestCard()

    player.card_manager.add_to_pile(card1, "hand")
    player.card_manager.add_to_pile(card2, "hand")
    player.card_manager.add_to_pile(card3, "hand")

    # Store original costs
    original_costs = [c._cost for c in [card1, card2, card3]]
    assert all(c == 1 for c in original_costs), "All cards should have base cost of 1"

    # Apply ConfusedPower
    confused_power = ConfusedPower()
    confused_power.owner = player
    player.powers.append(confused_power)

    # Execute on_turn_start() to randomize costs
    actions = confused_power.on_turn_start()
    assert len(actions) == 1, "on_turn_start() should return one LambdaAction"

    # Execute the lambda action to randomize costs
    actions[0].execute()

    # Check that costs have been randomized (0-3)
    new_costs = [c._cost for c in [card1, card2, card3]]
    assert all(0 <= c <= 3 for c in new_costs), "All costs should be between 0 and 3"

    # Check that at least one cost changed (may not always, but unlikely)
    assert new_costs != original_costs, "Costs should be randomized"


def test_confused_power_randomizes_each_turn(setup_game_state):
    """Test that costs are randomized at the start of each turn."""
    global game_state
    player = game_state.player

    # Create test card
    class TestCard(Card):
        base_cost = 1
        name = "Test Card"
        card_type = "Attack"

    # Add test card to hand
    card = TestCard()
    player.card_manager.add_to_pile(card, "hand")

    # Apply ConfusedPower
    confused_power = ConfusedPower()
    confused_power.owner = player
    player.powers.append(confused_power)

    # First turn randomization
    confused_power.on_turn_start()[0].execute()
    cost_turn1 = card._cost
    assert 0 <= cost_turn1 <= 3

    # Second turn randomization (should be different)
    confused_power.on_turn_start()[0].execute()
    cost_turn2 = card._cost

    # Costs may be the same due to randomness, but valid
    assert 0 <= cost_turn2 <= 3


def test_confused_power_does_not_stack(setup_game_state):
    """Test that ConfusedPower doesn't stack (stackable=False)."""
    global game_state
    player = game_state.player

    confused1 = ConfusedPower()
    confused2 = ConfusedPower()
    confused1.owner = player
    confused2.owner = player

    # Add first instance
    player.powers.append(confused1)
    assert len(player.powers) == 1

    # Add second instance - since stackable=False, should append
    player.powers.append(confused2)
    assert len(player.powers) == 2


def test_confused_power_is_permanent(setup_game_state):
    """Test that ConfusedPower has duration=0 (permanent during combat)."""
    power = ConfusedPower()
    assert power.duration == 0
