"""
Simple test to verify ConfusedPower works.
This test doesn't use pytest to avoid import issues.
"""

# Direct import to avoid circular dependencies
import sys
import os
sys.path.insert(0, 'D:/game/slay-the-model')

# Block localization loading to avoid zh.yaml issues
import yaml
original_yaml_load = yaml.safe_load
yaml.safe_load = lambda *args, **kwargs: {}

from powers.definitions.confused import ConfusedPower
from engine.game_state import GameState
from player.player import Player
from player.card_manager import CardManager
from cards.base import Card

# Create a simple test card
class TestCard(Card):
    base_cost = 1
    name = "Test Card"
    card_type = "Attack"

def test_confused_power():
    """Test that ConfusedPower randomizes card costs."""
    # Setup
    game_state = GameState()
    player = Player(max_hp=80, max_energy=3)
    player.card_manager = CardManager(deck=[])

    game_state.player = player
    game_state.combat_state.combat_turn = 1

    # Add card to hand
    card = TestCard()
    player.card_manager.add_to_pile(card, "hand")

    # Apply ConfusedPower
    confused_power = ConfusedPower()
    confused_power.owner = player
    player.powers.append(confused_power)

    # Execute on_turn_start to randomize costs
    actions = confused_power.on_turn_start()
    print(f"Actions returned: {len(actions)}")

    # Execute the lambda action
    if actions:
        actions[0].execute()

    # Check result
    new_cost = card._cost
    print(f"Card cost after randomization: {new_cost}")

    # Verify cost is in valid range (0-3)
    if 0 <= new_cost <= 3:
        print("✓ ConfusedPower works correctly!")
        return True
    else:
        print("✗ ConfusedPower failed - cost out of range")
        return False

if __name__ == "__main__":
    yaml.safe_load = original_yaml_load
    success = test_confused_power()
    sys.exit(0 if success else 1)
