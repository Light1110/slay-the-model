"""
Unit tests for Akabeko relic.
Tests first attack bonus (8 additional damage).
"""
import sys
sys.path.insert(0, 'D:/game/slay-the-model')

# Mock objects
class MockCard:
    def __init__(self):
        self._cost = 1
        self._damage = 5
        self.card_type = 'Attack'

class MockPlayer:
    def __init__(self):
        self.relics = []
        self.status_manager = MockStatusManager()
        self.powers = []

    def get_power(self, name):
        return None

class MockStatusManager:
    def __init__(self):
        self.status = None

def test_akabeko_relic():
    """Test Akabeko relic adds 8 damage to first attack."""
    from relics.global.common import Akabeko
    from engine.combat_state import CombatState

    relic = Akabeko()
    player = MockPlayer()

    # Test 1: Relic initializes with first_attack_played = False
    assert relic.first_attack_played is False, "Relic should init with first_attack_played = False"

    # Test 2: on_combat_start resets the flag
    from engine.game_state import game_state
    game_state.combat_state = CombatState()

    actions = relic.on_combat_start(player, entities=[])
    assert len(actions) == 1, "Should return one LambdaAction"

    # Execute to reset flag
    actions[0].execute()

    # Check flag is reset
    assert game_state.combat_state.turn_attack_cards_played == 0, "Combat start should reset first attack tracker"

    # Test 3: Simulate first attack card
    card = MockCard()
    player.relics.append(relic)

    # Reset turn info (but keep turn_attack_cards_played at 0)
    game_state.combat_state.reset_turn_info()

    # Simulate attack damage calculation
    # We need to mock resolve_card_value directly since it has dependencies
    from utils.dynamic_values import resolve_card_damage
    damage = resolve_card_damage(card, None)

    print(f"Test 3 - First attack damage: {damage}")
    assert damage == 13, f"First attack should deal 13 damage (5 base + 8 bonus)"

    # Test 4: Simulate second attack (should not get bonus)
    game_state.combat_state.turn_attack_cards_played += 1
    damage = resolve_card_damage(card, None)
    print(f"Test 4 - Second attack damage: {damage}")
    assert damage == 5, f"Second attack should deal 5 damage (no bonus)"

    print("All Akabeko tests PASSED")
    return True

if __name__ == "__main__":
    try:
        test_akabeko_relic()
        sys.exit(0)
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)
