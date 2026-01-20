"""
Neo blessing event.
"""

from events.base_event import Event, EventStage
from actions.display import DisplayTextAction, SelectAction
from actions.base import action_queue
from engine.game_state import game_state
from localization import t


class NeoEvent(Event):
    """Neo blessing event"""

    def __init__(self, callback=None, **kwargs):
        super().__init__(callback=callback, **kwargs)

    def build_stages(self):
        return [
            NeoBlessingStage("blessing_selection")
        ]


class NeoBlessingStage(EventStage):
    """Stage for Neo blessing selection"""

    def execute(self):
        super().execute()
        
        # Simple Neo blessing - just display a message and continue
        actions = [
            DisplayTextAction(text="Welcome to the Neo blessing!"),
            DisplayTextAction(text="You have received a blessing from Neo."),
        ]
        action_queue.add_actions(actions)
        
        # todo: 获得奖励
        
        # End the event after displaying messages
        self.event.end_event()