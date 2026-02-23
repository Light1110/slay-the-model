#!/usr/bin/env python
"""Tests for relic system."""

import unittest
from unittest.mock import Mock

from tests.test_combat_utils import CombatTestHelper
from engine.game_state import game_state
from relics.character.ironclad import BurningBlood


class TestRelics(unittest.TestCase):
    """Test relic functionality."""

    def setUp(self):
        self.helper = CombatTestHelper()
        self.player = self.helper.create_player(energy=3)
        self.helper.start_combat([])

    def test_burning_blood_creation(self):
        """Test BurningBlood relic can be created."""
        relic = BurningBlood()
        self.assertIsInstance(relic, BurningBlood)

    def test_relic_has_idstr(self):
        """Test relics have idstr attribute."""
        relic = BurningBlood()
        self.assertIsNotNone(relic.idstr)


if __name__ == "__main__":
    unittest.main()
