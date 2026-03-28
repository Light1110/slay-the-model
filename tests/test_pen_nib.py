"""Test PenNib relic functionality."""
import unittest
from unittest.mock import MagicMock

from relics.global_relics.common import PenNib
from utils.types import CardType, RarityType
from actions.combat import ApplyPowerAction
from engine.game_state import game_state


class TestPenNib(unittest.TestCase):
    """Test PenNib relic: Every 10th Attack deals double damage."""

    def setUp(self):
        """Set up test fixtures."""
        self.pen_nib = PenNib()
        self.player = MagicMock()
        self.entities = []
        game_state.action_queue.clear()

    def test_pen_nib_initialization(self):
        """Test PenNib initializes correctly."""
        self.assertEqual(self.pen_nib.attacks_played, 0)
        self.assertEqual(self.pen_nib.rarity, RarityType.COMMON)

    def test_pen_nib_resets_on_combat_start(self):
        """Test attack counter resets on combat start."""
        self.pen_nib.attacks_played = 15
        self.pen_nib.on_combat_start(self.player, self.entities)
        
        self.assertEqual(self.pen_nib.attacks_played, 0)
        self.assertTrue(game_state.action_queue.is_empty())

    def test_pen_nib_tracks_attacks(self):
        """Test PenNib tracks attacks played."""
        # Create mock attack card
        attack_card = MagicMock()
        attack_card.card_type = CardType.ATTACK
        
        # Play 5 attacks
        for _ in range(5):
            self.pen_nib.on_card_play(attack_card, self.player, self.entities)
        
        self.assertEqual(self.pen_nib.attacks_played, 5)

    def test_pen_nib_ignores_non_attacks(self):
        """Test PenNib ignores non-attack cards."""
        skill_card = MagicMock()
        skill_card.card_type = CardType.SKILL
        
        self.pen_nib.on_card_play(skill_card, self.player, self.entities)
        
        self.assertEqual(self.pen_nib.attacks_played, 0)

    def test_pen_nib_applies_power_on_10th_attack(self):
        """Test PenNib applies PenNibPower on 10th attack."""
        attack_card = MagicMock()
        attack_card.card_type = CardType.ATTACK
        
        # Play 9 attacks - should not trigger
        for _ in range(9):
            self.pen_nib.on_card_play(attack_card, self.player, self.entities)
            self.assertTrue(game_state.action_queue.is_empty())
        
        # 10th attack should trigger PenNibPower
        self.pen_nib.on_card_play(attack_card, self.player, self.entities)
        self.assertEqual(len(game_state.action_queue.queue), 1)
        self.assertIsInstance(game_state.action_queue.queue[0], ApplyPowerAction)
        from powers.definitions.pen_nib import PenNibPower
        self.assertIsInstance(getattr(game_state.action_queue.queue[0], "power", None), PenNibPower)

    def test_pen_nib_applies_power_on_20th_attack(self):
        """Test PenNib applies PenNibPower on 20th attack."""
        attack_card = MagicMock()
        attack_card.card_type = CardType.ATTACK
        
        # Play 20 attacks
        for i in range(20):
            self.pen_nib.on_card_play(attack_card, self.player, self.entities)
            if (i + 1) % 10 == 0:
                # 10th and 20th should trigger
                self.assertEqual(len(game_state.action_queue.queue), 1)
                self.assertIsInstance(game_state.action_queue.queue[0], ApplyPowerAction)
                game_state.action_queue.clear()
            else:
                self.assertTrue(game_state.action_queue.is_empty())


if __name__ == '__main__':
    unittest.main()
