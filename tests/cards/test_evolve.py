from entities.creature import Creature
"""Comprehensive tests for Evolve card."""
import unittest
from utils.types import CardType, RarityType
from actions.card import DrawCardsAction
from cards.colorless.wound import Wound
from cards.ironclad.evolve import Evolve
from cards.ironclad.strike import Strike
from enemies.act1.cultist import Cultist
from tests.test_combat_utils import create_test_helper
from utils.types import PilePosType


class TestEvolve(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        card = Evolve()
        self.assertEqual(card.cost, 1)
        self.assertEqual(card.card_type, CardType.POWER)
        self.assertEqual(card.rarity, RarityType.UNCOMMON)

    def test_applies_power(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = Evolve()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)
        
        # Check that Evolve power was applied
        powers = self.helper.game_state.player.powers
        power_names = [type(p).__name__ for p in powers]
        self.assertIn("EvolvePower", power_names)

    def test_energy_cost(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        
        card = Evolve()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=None)
        
        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 1)

    def test_description_uses_magic_draw(self):
        card = Evolve()
        self.assertIn("draw 1", card.description.resolve())
        card.upgrade()
        self.assertIn("draw 2", card.description.resolve())

    def test_upgraded_draws_two_cards_when_status_is_drawn(self):
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])
        player.card_manager.get_pile("draw_pile").clear()
        player.card_manager.get_pile("hand").clear()
        player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
        player.card_manager.add_to_pile(Strike(), "draw_pile", PilePosType.TOP)
        player.card_manager.add_to_pile(Wound(), "draw_pile", PilePosType.TOP)

        card = Evolve()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=None)

        power = player.get_power("Evolve")
        self.assertIsNotNone(power)
        assert power is not None
        self.assertEqual(power.amount, 2)

        DrawCardsAction(count=1).execute()
        self.helper.game_state.drive_actions()
        hand = player.card_manager.get_pile("hand")
        self.assertEqual(len(hand), 3)
        self.assertEqual(sum(1 for drawn in hand if drawn.card_type == CardType.STATUS), 1)


if __name__ == '__main__':
    unittest.main()
