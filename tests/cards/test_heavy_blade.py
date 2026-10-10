from entities.creature import Creature
"""Comprehensive tests for Heavy Blade card."""
import unittest
from actions.combat_cards import PlayCardBHAction
from tests.test_combat_utils import create_test_helper
from cards.ironclad.heavy_blade import HeavyBlade
from enemies.act1.cultist import Cultist
from powers.definitions.strength import StrengthPower
from powers.definitions.weak import WeakPower
from utils.dynamic_values import resolve_card_damage
from utils.types import CardType, RarityType


class TestHeavyBlade(unittest.TestCase):
    def setUp(self):
        self.helper = create_test_helper()

    def tearDown(self):
        self.helper._reset_game_state()

    def test_basic_properties(self):
        """Test Heavy Blade has correct basic properties."""
        card = HeavyBlade()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.base_damage, 14)
        self.assertEqual(card.card_type, CardType.ATTACK)
        self.assertEqual(card.rarity, RarityType.COMMON)
        self.assertIn("strength_mult", card._magic)
        self.assertEqual(card._magic["strength_mult"], 3)

    def test_deals_damage(self):
        """Test Heavy Blade deals damage to enemy."""
        player = self.helper.create_player()
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])

        card = HeavyBlade()
        self.helper.add_card_to_hand(card)
        self.helper.play_card(card, target=enemy)

        self.assertEqual(enemy.hp, 36)

    def test_upgraded(self):
        """Test upgraded Heavy Blade has more damage and multiplier."""
        card = HeavyBlade()
        card.upgrade()
        self.assertEqual(card.cost, 2)
        self.assertEqual(card.damage, 14)
        self.assertEqual(card._magic["strength_mult"], 5)

    def test_energy_cost(self):
        """Test Heavy Blade costs 2 energy."""
        player = self.helper.create_player(energy=3)
        enemy = self.helper.create_enemy(Cultist)
        self.helper.start_combat([enemy])

        card = HeavyBlade()
        self.helper.add_card_to_hand(card)
        initial_energy = self.helper.game_state.player.energy
        self.helper.play_card(card, target=enemy)

        self.assertEqual(self.helper.game_state.player.energy, initial_energy - 2)

    def test_strength_applies_three_times_on_play(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        player.energy = 3
        player.add_power(StrengthPower(amount=3))

        card = HeavyBlade()
        self.helper.add_card_to_hand(card)
        self.assertEqual(resolve_card_damage(card, target=enemy), 23)

        PlayCardBHAction(card, [enemy]).execute()
        self.helper.game_state.drive_actions()
        self.assertEqual(enemy.hp, 27)

    def test_upgraded_strength_applies_five_times_on_play(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        player.energy = 3
        player.add_power(StrengthPower(amount=3))

        card = HeavyBlade()
        card.upgrade()
        self.helper.add_card_to_hand(card)
        self.assertEqual(card.damage, 14)
        self.assertEqual(resolve_card_damage(card, target=enemy), 29)

        PlayCardBHAction(card, [enemy]).execute()
        self.helper.game_state.drive_actions()
        self.assertEqual(enemy.hp, 21)

    def test_weak_floors_after_tripled_strength(self):
        player = self.helper.create_player(hp=80, energy=3)
        enemy = self.helper.create_enemy(Cultist, hp=50)
        self.helper.start_combat([enemy])
        player.energy = 3
        player.add_power(StrengthPower(amount=3))
        player.add_power(WeakPower(duration=2))

        card = HeavyBlade()
        self.helper.add_card_to_hand(card)
        self.assertEqual(resolve_card_damage(card, target=enemy), 17)

        PlayCardBHAction(card, [enemy]).execute()
        self.helper.game_state.drive_actions()
        self.assertEqual(enemy.hp, 33)


if __name__ == '__main__':
    unittest.main()
