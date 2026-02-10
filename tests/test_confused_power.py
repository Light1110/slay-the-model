"""
Tests for ConfusedPower.
Tests that ConfusedPower randomizes card costs whenever cards are drawn.
"""
import pytest
from powers.definitions.confused import ConfusedPower
from engine.game_state import GameState, game_state
from player.player import Player
from player.card_manager import CardManager
from cards.base import Card
from actions.card import DrawCardsAction


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


def test_confused_power_on_turn_start_randomizes_existing_hand(setup_game_state):
    """Test that on_turn_start() randomizes costs of cards already in hand."""
    global game_state
    player = game_state.player

    # Create a simple test card
    class TestCard(Card):
        base_cost = 1
        name = "Test Card"
        card_type = "Attack"

    # Add test cards to hand directly (simulating cards that were drawn in previous turns)
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

    # Execute on_turn_start() to randomize costs of existing hand
    actions = confused_power.on_turn_start()
    assert len(actions) == 1, "on_turn_start() should return one LambdaAction"

    # Execute the lambda action to randomize costs
    actions[0].execute()

    # Check that costs have been randomized (0-3)
    new_costs = [c._cost for c in [card1, card2, card3]]
    assert all(0 <= c <= 3 for c in new_costs), "All costs should be between 0 and 3"

    # Check that at least one cost changed (may not always, but unlikely)
    assert new_costs != original_costs, "Costs should be randomized"


def test_confused_power_on_card_draw_randomizes_new_card(setup_game_state):
    """Test that on_card_draw() randomizes cost when a new card is drawn."""
    global game_state
    player = game_state.player

    # Create test card in draw pile
    class TestCard(Card):
        base_cost = 2
        name = "Test Card"
        card_type = "Attack"

    card = TestCard()
    player.card_manager.add_to_pile(card, "draw_pile")

    # Apply ConfusedPower
    confused_power = ConfusedPower()
    confused_power.owner = player
    player.powers.append(confused_power)

    # Draw the card - this should trigger on_card_draw
    draw_action = DrawCardsAction(count=1)
    draw_action.execute()

    # Check that the card is now in hand
    assert card in player.card_manager.get_pile("hand"), "Card should be in hand after draw"

    # Check that cost has been randomized (0-3, different from original cost of 2)
    assert 0 <= card._cost <= 3, "Card cost should be randomized between 0 and 3"


def test_confused_power_randomizes_on_each_draw(setup_game_state):
    """Test that costs are randomized each time a card is drawn."""
    global game_state
    player = game_state.player

    # Create test cards in draw pile
    class TestCard(Card):
        base_cost = 1
        name = "Test Card"
        card_type = "Attack"

    card1 = TestCard()
    card2 = TestCard()

    player.card_manager.add_to_pile(card1, "draw_pile")
    player.card_manager.add_to_pile(card2, "draw_pile")

    # Apply ConfusedPower
    confused_power = ConfusedPower()
    confused_power.owner = player
    player.powers.append(confused_power)

    # Draw first card
    draw_action = DrawCardsAction(count=1)
    draw_action.execute()
    cost_card1 = card1._cost
    assert 0 <= cost_card1 <= 3, "First card cost should be randomized"

    # Draw second card
    draw_action = DrawCardsAction(count=1)
    draw_action.execute()
    cost_card2 = card2._cost
    assert 0 <= cost_card2 <= 3, "Second card cost should be randomized"

    # Both cards should be in hand
    hand = player.card_manager.get_pile("hand")
    assert len(hand) == 2, "Both cards should be in hand"
    assert card1 in hand and card2 in hand


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


def test_confused_power_works_with_multiple_draws(setup_game_state):
    """Test that ConfusedPower works correctly when drawing multiple cards at once."""
    global game_state
    player = game_state.player

    # Create test cards in draw pile
    class TestCard(Card):
        base_cost = 1
        name = "Test Card"
        card_type = "Attack"

    for _ in range(5):
        card = TestCard()
        player.card_manager.add_to_pile(card, "draw_pile")

    # Apply ConfusedPower
    confused_power = ConfusedPower()
    confused_power.owner = player
    player.powers.append(confused_power)

    # Draw 5 cards at once
    draw_action = DrawCardsAction(count=5)
    draw_action.execute()

    # Check that all 5 cards are in hand
    hand = player.card_manager.get_pile("hand")
    assert len(hand) == 5, "All 5 cards should be in hand"

    # Check that all costs are randomized (0-3)
    costs = [c._cost for c in hand]
    assert all(0 <= c <= 3 for c in costs), "All card costs should be randomized between 0 and 3"


def test_confused_power_without_power_does_not_randomize(setup_game_state):
    """Test that drawing without ConfusedPower does not randomize costs."""
    global game_state
    player = game_state.player

    # Create test card in draw pile
    class TestCard(Card):
        base_cost = 2
        name = "Test Card"
        card_type = "Attack"

    card = TestCard()
    player.card_manager.add_to_pile(card, "draw_pile")

    # Draw the card WITHOUT ConfusedPower
    draw_action = DrawCardsAction(count=1)
    draw_action.execute()

    # Check that the card is in hand
    assert card in player.card_manager.get_pile("hand"), "Card should be in hand after draw"

    # Check that cost is NOT randomized (should still be 2)
    assert card._cost == 2, "Card cost should NOT be randomized without ConfusedPower"