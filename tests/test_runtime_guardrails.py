import pytest

from entities.creature import Creature
from player.player_factory import create_player


UNIMPLEMENTED_SILENT_ERROR = "Character 'Silent' is not playable yet: starter cards are unavailable"


def test_take_damage_rejects_list_input():
    creature = Creature(max_hp=10)

    with pytest.raises(TypeError, match="take_damage expects int"):
        creature.take_damage([3])


def test_create_player_rejects_unimplemented_character_starter_cards():
    with pytest.raises(ValueError, match=UNIMPLEMENTED_SILENT_ERROR):
        create_player("Silent")
