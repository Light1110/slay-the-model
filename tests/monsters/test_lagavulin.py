#!/usr/bin/env python
"""Tests for Lagavulin enemy."""

import unittest
from unittest.mock import Mock

from tests.test_combat_utils import CombatTestHelper
from enemies.act1.lagavulin import Lagavulin
from engine.game_state import game_state


class TestLagavulin(unittest.TestCase):
    """Test Lagavulin enemy functionality."""

    def setUp(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player(energy=3)
        self.enemy = self.helper.create_enemy(Lagavulin, hp=110)

    def test_lagavulin_creation(self):
        """Test Lagavulin can be created."""
        self.assertIsInstance(self.enemy, Lagavulin)

    def test_lagavulin_has_intentions(self):
        """Test Lagavulin has intentions defined."""
        self.assertIsNotNone(self.enemy.intentions)

    def test_lagavulin_intention_on_combat_start(self):
        """Test Lagavulin starts with sleep intention."""
        self.enemy.on_combat_start(floor=1)
        self.assertIsNotNone(self.enemy.current_intention)
        self.assertEqual(self.enemy.current_intention.name, "sleep")

    def test_attack_pattern_after_wake(self):
        """Test Lagavulin attacks after waking from sleep."""
        # Create fresh enemy and start combat manually
        enemy = Lagavulin()
        enemy.on_combat_start(floor=1)
        
        # First intention is sleep
        self.assertEqual(enemy.current_intention.name, "sleep")

        # Second turn (still sleeping)
        enemy.on_player_turn_start()
        self.assertEqual(enemy.current_intention.name, "sleep")

        # Third turn (now attacks)
        enemy.on_player_turn_start()
        self.assertEqual(enemy.current_intention.name, "attack")

    def test_lagavulin_has_hp(self):
        """Test Lagavulin has correct HP."""
        self.assertEqual(self.enemy.hp, 110)


if __name__ == "__main__":
    unittest.main()
