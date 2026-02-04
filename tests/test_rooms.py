"""
Test suite for room implementations (RestRoom, ShopRoom, TreasureRoom).
"""
import pytest
from map.map_manager import MapManager
from rooms.rest import RestRoom
from rooms.shop import ShopRoom
from rooms.treasure import TreasureRoom
from utils.types import RoomType


class TestRestRoom:
    """Test RestRoom functionality."""

    def test_rest_room_creation(self):
        """Test that RestRoom can be instantiated."""
        rest_room = RestRoom()
        assert rest_room is not None
        assert rest_room.localization_prefix == "rooms"

    def test_rest_room_options(self):
        """Test that rest room creates options."""
        rest_room = RestRoom()
        # Mock game_state for testing
        # In real tests, would need proper setup
        # This is a basic sanity check
        assert hasattr(rest_room, '_create_options')

    def test_rest_has_relic_check(self):
        """Test relic checking logic."""
        rest_room = RestRoom()
        assert hasattr(rest_room, '_has_relic')


class TestShopRoom:
    """Test ShopRoom functionality."""

    def test_shop_room_creation(self):
        """Test that ShopRoom can be instantiated."""
        shop_room = ShopRoom()
        assert shop_room is not None
        assert shop_room.localization_prefix == "rooms"
        assert shop_room.card_removal_price == 75
        assert not shop_room.card_removal_used

    def test_shop_item_creation(self):
        """Test ShopItem creation and pricing."""
        from rooms.shop import ShopItem
        from utils.types import RarityType

        # Create a mock item
        mock_item = "TestCard"
        shop_item = ShopItem("card", mock_item, 100, discount=0.5)

        assert shop_item.item_type == "card"
        assert shop_item.item == mock_item
        assert shop_item.base_price == 100
        assert shop_item.discount == 0.5
        assert not shop_item.purchased

    def test_shop_item_price_calculation(self):
        """Test price calculation with ascension and discounts."""
        from rooms.shop import ShopItem

        shop_item = ShopItem("card", "TestCard", 100, discount=0)

        # Base price
        assert shop_item.get_final_price(ascension_level=0) == 100

        # Ascension 16: 10% more expensive
        price_asc16 = shop_item.get_final_price(ascension_level=16)
        assert price_asc16 == 110

        # With 50% discount
        shop_item.discount = 0.5
        price_discounted = shop_item.get_final_price(ascension_level=0)
        assert price_discounted == 50

    def test_shop_generation_methods(self):
        """Test shop item generation methods exist."""
        shop_room = ShopRoom()
        assert hasattr(shop_room, '_generate_items')
        assert hasattr(shop_room, '_generate_colored_cards')
        assert hasattr(shop_room, '_generate_colorless_cards')
        assert hasattr(shop_room, '_generate_potions')
        assert hasattr(shop_room, '_generate_relics')


class TestTreasureRoom:
    """Test TreasureRoom functionality."""

    def test_treasure_room_creation(self):
        """Test that TreasureRoom can be instantiated."""
        treasure_room = TreasureRoom()
        assert treasure_room is not None
        assert not treasure_room.is_boss
        assert treasure_room.chest_type is None
        assert not treasure_room.chest_opened

    def test_boss_treasure_room_creation(self):
        """Test that boss treasure room can be instantiated."""
        boss_treasure = TreasureRoom(is_boss=True)
        assert boss_treasure is not None
        assert boss_treasure.is_boss

    def test_chest_type_determination(self):
        """Test chest type probabilities."""
        treasure_room = TreasureRoom()

        # Run multiple tests to check probabilities
        chest_types = []
        for _ in range(100):
            chest_type = treasure_room._determine_chest_type()
            chest_types.append(chest_type)

        # Check that all types are possible
        assert "small" in chest_types
        assert "medium" in chest_types
        assert "large" in chest_types

        # Check approximate probabilities
        small_count = chest_types.count("small")
        medium_count = chest_types.count("medium")
        large_count = chest_types.count("large")

        # Small: ~50%, Medium: ~33%, Large: ~17%
        assert 40 <= small_count <= 60
        assert 25 <= medium_count <= 45
        assert 10 <= large_count <= 25

    def test_small_chest_contents(self):
        """Test small chest contents generation."""
        treasure_room = TreasureRoom()
        treasure_room.chest_type = "small"

        contents = treasure_room._get_small_chest_contents()

        assert "gold" in contents
        assert "relic" in contents
        assert "relics" in contents

        # Either gold OR relic, not both
        has_gold = contents.get("gold", 0) > 0
        has_relic = contents.get("relic") is not None
        assert has_gold or has_relic

        # If gold, should be in range 23-27
        if has_gold:
            assert 23 <= contents["gold"] <= 27

    def test_medium_chest_contents(self):
        """Test medium chest contents generation."""
        treasure_room = TreasureRoom()
        treasure_room.chest_type = "medium"

        contents = treasure_room._get_medium_chest_contents()

        assert "gold" in contents
        assert "relic" in contents
        assert "relics" in contents

        # Either gold OR relic
        has_gold = contents.get("gold", 0) > 0
        has_relic = contents.get("relic") is not None
        assert has_gold or has_relic

        # If gold, should be in range 45-55
        if has_gold:
            assert 45 <= contents["gold"] <= 55

    def test_large_chest_contents(self):
        """Test large chest contents generation."""
        treasure_room = TreasureRoom()
        treasure_room.chest_type = "large"

        contents = treasure_room._get_large_chest_contents()

        assert "gold" in contents
        assert "relic" in contents
        assert "relics" in contents

        # Either gold OR relic
        has_gold = contents.get("gold", 0) > 0
        has_relic = contents.get("relic") is not None
        assert has_gold or has_relic

        # If gold, should be in range 68-82
        if has_gold:
            assert 68 <= contents["gold"] <= 82

    def test_boss_chest_contents(self):
        """Test boss chest contents generation."""
        treasure_room = TreasureRoom(is_boss=True)
        treasure_room.chest_type = "boss"

        contents = treasure_room._get_boss_chest_contents()

        assert "gold" in contents
        assert "relic" in contents
        assert "relics" in contents

        # Boss chest should have 3 relics (or 4 with Matryoshka)
        relics = contents.get("relics", [])
        assert len(relics) == 3

        # No gold in boss chest (it's relic selection)
        assert contents.get("gold", 0) == 0


class TestMapManagerRoomCreation:
    """Test MapManager's room creation with new room types."""

    def test_create_rest_room(self):
        """Test that MapManager creates RestRoom correctly."""
        map_manager = MapManager(seed=12345)
        room = map_manager._create_room_instance(RoomType.REST)

        assert isinstance(room, RestRoom)

    def test_create_shop_room(self):
        """Test that MapManager creates ShopRoom correctly."""
        map_manager = MapManager(seed=12345)
        room = map_manager._create_room_instance(RoomType.MERCHANT)

        assert isinstance(room, ShopRoom)

    def test_create_treasure_room(self):
        """Test that MapManager creates TreasureRoom correctly."""
        map_manager = MapManager(seed=12345)
        room = map_manager._create_room_instance(RoomType.TREASURE)

        assert isinstance(room, TreasureRoom)

    def test_create_boss_room(self):
        """Test that MapManager creates TreasureRoom with is_boss=True for BOSS type."""
        map_manager = MapManager(seed=12345)
        room = map_manager._create_room_instance(RoomType.BOSS)

        assert isinstance(room, TreasureRoom)
        assert room.is_boss is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])