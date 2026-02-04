"""
Treasure room implementation.
"""
import random
from actions.base import Action, action_queue
from actions.display import SelectAction
from actions.treasure import OpenChestAction, SkipTreasureAction, _has_relic
from engine.game_state import game_state
from localization import LocalStr, t
from rooms.base import Room
from utils.option import Option
from utils.registry import register


@register("room")
class TreasureRoom(Room):
    """Treasure room where player can open chests"""

    def __init__(self, is_boss=False, **kwargs):
        super().__init__(**kwargs)
        self.localization_prefix = "rooms"
        self.is_boss = is_boss
        self.chest_type = None
        self.chest_opened = False

    def enter_room(self):
        """Enter treasure room"""
        super().enter_room()

        # Determine chest type
        if self.is_boss:
            self.chest_type = "boss"
        else:
            roll = random.random()
            self.chest_type = "small" if roll < 0.50 else "medium" if roll < 0.83 else "large"

        # Create options
        options = []

        # Open chest option
        if not self.chest_opened:
            if self.is_boss:
                name = self.local("TreasureRoom.open_boss_chest")
            else:
                name = self.local("TreasureRoom.open_chest", chest_type=self.chest_type)
            options.append(Option(name=name, actions=[OpenChestAction(self)]))

        # Skip option (only for boss chests)
        if self.is_boss:
            options.append(Option(
                name=self.local("TreasureRoom.skip"),
                actions=[SkipTreasureAction()]
            ))

        # Add selection action
        action_queue.add_action(SelectAction(
            title=self.local("TreasureRoom.boss_title") if self.is_boss else self.local("TreasureRoom.title"),
            options=options
        ))
