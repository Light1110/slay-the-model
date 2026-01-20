"""
Combat event flow.
"""
from engine.game_state import game_state
from rooms.base import Room
from utils.registry import register


@register("room")
class CombatRoom(Room):
    """Combat room"""

    def __init__(self, enemies=None, **kwargs):
        self.enemies = enemies or []
        super().__init__(**kwargs)

    def enter_room(self):
        """Enter the combat room"""
        super().enter_room()
        # Simple combat - just display a message
        print("Entering combat room...")