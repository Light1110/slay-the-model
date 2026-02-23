"""Tests for combat room reward behavior."""

import unittest
from unittest.mock import Mock

from actions.card import ChooseAddRandomCardAction
from actions.reward import AddGoldAction, AddRandomPotionAction
from engine.game_state import game_state
from rooms.combat import CombatRoom
from utils.types import RoomType


class TestCombatRoomRewards(unittest.TestCase):
    """Test reward rules for combat room victory."""

    def setUp(self):
        game_state._initialized = False
        game_state.__init__()
        game_state.player = Mock()
        game_state.player.relics = []

    def test_act3_boss_victory_has_no_reward_actions(self):
        """Act 3 boss victory should not generate combat rewards."""
        game_state.current_act = 3
        room = CombatRoom(enemies=[], room_type=RoomType.BOSS)

        actions = room._handle_victory()

        self.assertTrue(actions)
        self.assertFalse(any(isinstance(a, AddGoldAction) for a in actions))
        self.assertFalse(any(isinstance(a, ChooseAddRandomCardAction)
                             for a in actions))
        self.assertFalse(any(isinstance(a, AddRandomPotionAction)
                             for a in actions))

    def test_act4_boss_victory_has_no_reward_actions(self):
        """Act 4 boss victory should not generate combat rewards."""
        game_state.current_act = 4
        room = CombatRoom(enemies=[], room_type=RoomType.BOSS)

        actions = room._handle_victory()

        self.assertTrue(actions)
        self.assertFalse(any(isinstance(a, AddGoldAction) for a in actions))
        self.assertFalse(any(isinstance(a, ChooseAddRandomCardAction)
                             for a in actions))
        self.assertFalse(any(isinstance(a, AddRandomPotionAction)
                             for a in actions))


if __name__ == "__main__":
    unittest.main()
