"""
Neo reward room.
"""
from actions import action_queue
from actions.misc import StartEventAction
from engine.game_state import game_state
from rooms.base import Room
from utils.registry import register
from events.neo_event import NeoEvent


@register("room")
class NeoRewardRoom(Room):
    """Neo reward blessing room"""

    def enter_room(self):
        """Enter the Neo blessing room"""
        super().enter_room()
        # Create Neo blessing event
        neo_event = NeoEvent(callback=self.leave_room)
        game_state.event_stack.append(neo_event)
        action_queue.add_action(StartEventAction())