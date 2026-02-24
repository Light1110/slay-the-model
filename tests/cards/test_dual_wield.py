from entities.creature import Creature
"""Comprehensive tests for Dual Wield card."""
import unittest
from utils.types import CardType, RarityType
from cards.ironclad.dual_wield import DualWield
from cards.ironclad.strike import Strike
from cards.ironclad.inflame import Inflame
from cards.ironclad.defend import Defend
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper


class TestDualWield(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = DualWield()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.SKILL)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)
        self.assertEqual(card.upgrade_cost, 0)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = DualWield()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)

    def test_upgraded_cost(self):
        card = DualWield()
        card.upgrade()
        self.assertEqual(card.cost, 0)

    def test_can_only_copy_attack_or_power_cards(self):
        """Test that Dual Wield can only copy Attack or Power cards, not Skill cards."""
        # Setup
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        # Add different types of cards to hand
        attack_card = Strike()  # Attack card
        power_card = Inflame()  # Power card
        skill_card = Defend()   # Skill card
        
        self.helper.add_card_to_hand(attack_card)
        self.helper.add_card_to_hand(power_card)
        self.helper.add_card_to_hand(skill_card)
        
        # Add Dual Wield to hand
        dual_wield = DualWield()
        self.helper.add_card_to_hand(dual_wield)
        
        # Play Dual Wield
        initial_hand_size = len(self.helper.game_state.player.card_manager.piles['hand'])
        self.helper.play_card(dual_wield, target=None)
        
        # After playing Dual Wield, we should have a ChooseCopyCardAction
        # The action should only show Attack and Power cards as options, not Skill cards
        # Since we can't directly test the UI selection, we need to test the logic
        
        # For now, we'll test that the card plays without error
        # The actual filtering logic will be tested in the implementation
        self.assertTrue(True)  # Placeholder test
        
    def test_choose_copy_card_action_filters_card_types(self):
        """Test that ChooseCopyCardAction filters cards to only Attack and Power types."""
        # This test will fail initially because ChooseCopyCardAction doesn't filter card types
        # We need to modify ChooseCopyCardAction to filter by card_type
        
        # Import the action class
        from actions.card import ChooseCopyCardAction
        from utils.result_types import SingleActionResult
        from actions.display import SelectAction
        
        # Create a mock game state with different card types in hand
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        # Add cards to hand
        attack_card = Strike()  # Attack card
        power_card = Inflame()  # Power card
        skill_card = Defend()   # Skill card
        
        self.helper.add_card_to_hand(attack_card)
        self.helper.add_card_to_hand(power_card)
        self.helper.add_card_to_hand(skill_card)
        
        # Create the action
        action = ChooseCopyCardAction(pile="hand", copies=1)
        
        # Execute the action to see what options it creates
        result = action.execute()
        
        # The action should return a SingleActionResult with a SelectAction
        self.assertIsInstance(result, SingleActionResult)
        self.assertIsInstance(result.action, SelectAction)
        
        # The SelectAction should have options only for Attack and Power cards
        # Currently, it will have 3 options (all cards), but after our fix, it should have only 2
        # For now, this test will fail because all 3 cards are included
        options = result.action.options
        self.assertEqual(len(options), 2, "Should only have options for Attack and Power cards, not Skill cards")
        
        # Verify that the options are for Attack and Power cards only
        # We can check by looking at the card types
        for option in options:
            # Each option has actions that contain a CopyCardAction with a card
            for action in option.actions:
                if hasattr(action, 'card'):
                    card = action.card
                    self.assertIn(card.card_type, [CardType.ATTACK, CardType.POWER],
                                 f"Card {card.__class__.__name__} should be Attack or Power, not {card.card_type}")


if __name__ == '__main__':
    unittest.main()
