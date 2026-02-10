"""
Test for Tiny Chest relic functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from utils.types import RoomType


class TestTinyChestRelic:
    """Test Tiny Chest relic."""

    @patch('utils.registry.list_registered')
    def test_relic_registered(self, mock_list):
        """Test that Tiny Chest relic is registered."""
        mock_list.return_value = ["tiny_chest"]

        from utils.registry import list_registered, get_registered
        assert "tiny_chest" in list_registered("relic")

    @patch('engine.game_state.game_state')
    @patch('utils.result_types.NoneResult')
    @patch('utils.registry.get_registered')
    def test_on_map_enter_increments_counter(self, mock_gs, mock_none, mock_list):
        """Test that on_map_enter increments counter."""
        # Setup mock game state
        mock_gs.unknown_room_visits = {}
        mock_gs.unknown_room_visits[RoomType.TREASURE] = 0

        mock_list.return_value = ["tiny_chest"]

        # Create relic class mock
        mock_relic_cls = MagicMock()
        mock_relic_instance = MagicMock()
        mock_relic_instance.unknown_room_count = 0
        mock_relic_cls.return_value = mock_relic_instance
        mock_none.return_value = NoneResult()

        from utils.registry import get_registered
        mock_get = MagicMock(return_value=mock_relic_cls)

        # Import and create relic
        from utils.types import CardType, RarityType
        from relics.base import Relic
        from utils.registry import register

        # Re-register to inject mock
        register("relic", lambda: mock_relic_instance)(relic_class="tiny_chest")

        # Import map manager and test
        from map.map_manager import MapManager
        map_manager = MapManager(seed=42, act_id=1)

        # Call on_map_enter
        mock_map_data = MagicMock()
        mock_map_data.current_floor = 5
        actions = mock_relic_instance.on_map_enter(mock_map_data)

        # Counter should be incremented
        assert mock_relic_instance.unknown_room_count == 1

        # Only one action (NoneResult)
        assert len(actions) == 1
        assert actions[0] == mock_none.return_value

    @patch('engine.game_state.game_state')
    @patch('utils.result_types.NoneResult')
    @patch('utils.registry.get_registered')
    def test_forces_treasure_every_4th_room(self, mock_gs, mock_none, mock_list):
        """Test that treasure room is forced every 3rd ? visit."""
        # Setup mock game state
        mock_gs.unknown_room_visits = {}
        mock_gs.unknown_room_visits[RoomType.TREASURE] = 0

        mock_list.return_value = ["tiny_chest"]

        # Create relic instance
        mock_relic_cls = MagicMock()
        mock_relic_instance = MagicMock()
        mock_relic_instance.unknown_room_count = 0
        mock_relic_cls.return_value = mock_relic_instance
        mock_none.return_value = NoneResult()

        from utils.registry import get_registered
        mock_get = MagicMock(return_value=mock_relic_cls)
        from utils.registry import register

        # Re-register to inject mock
        register("relic", lambda: mock_relic_instance)(relic_class="tiny_chest")

        # Import and create map manager
        from map.map_manager import MapManager
        map_manager = MapManager(seed=42, act_id=1)

        mock_map_data = MagicMock()

        # Call on_map_enter 3 times (should not force treasure)
        for i in range(3):
            mock_relic_instance.unknown_room_count = i
            actions = mock_relic_instance.on_map_enter(mock_map_data)

        # Should not force treasure yet (counter not divisible by 3)
        assert len(actions) == 1  # Just NoneResult

        # Verify treasure counter was not reset
        assert mock_gs.unknown_room_visits[RoomType.TREASURE] == 0

        # Call 4th time (should force treasure)
        mock_relic_instance.unknown_room_count = 3
        actions = mock_relic_instance.on_map_enter(mock_map_data)

        # Should force treasure room (NoneResult resets treasure counter)
        assert len(actions) == 1
        assert actions[0] == mock_none.return_value

        # Verify treasure counter was reset to 0
        assert mock_gs.unknown_room_visits[RoomType.TREASURE] == 0

        # Verify counter was reset after forcing treasure
        assert mock_relic_instance.unknown_room_count == 0
