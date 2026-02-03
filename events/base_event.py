"""
Base event definitions for the new architecture.
"""
from engine.game_state import game_state
from localization import Localizable
class Event(Localizable):
    """Base event class - contains multiple stages"""

    def __init__(self, callback=None, **kwargs):
        self.callback = callback
        self.kwargs = kwargs
        self.current_stage = None
        self.stages = self.build_stages()
        # Set event reference on each stage
        for stage in self.stages:
            stage.event = self

    def build_stages(self):
        """Build the stages for this event - to be overridden"""
        return []

    def start_event(self):
        """Start the event by setting the initial stage and executing its actions"""
        if game_state.config.debug:
            print(f"Starting event: {self}")
        if self.stages:
            self.current_stage = self.stages[0]
            self.current_stage.execute()

    def transition_to_stage(self, stage_name):
        """Transition to a specific stage and execute its actions"""
        if game_state.config.debug:
            print(f"Transitioning to stage: {stage_name}")
        for stage in self.stages:
            if stage.stage_name == stage_name:
                self.current_stage = stage
                self.current_stage.execute()
                return
        # If stage not found, end event
        self.end_event()

    def end_event(self):
        """End the event"""
        if game_state.config.debug:
            print(f"Ending event: {self}")
        self.current_stage = None
        # Call callback if provided
        if self.callback:
            self.callback()
            
    def __str__(self):
        return f"{self.__class__.__name__}()"


class EventStage(Localizable):
    """Base class for event stages"""

    def __init__(self, stage_name):
        self.stage_name = stage_name
        self.event = None  # Will be set by Event

    def execute(self):
        """Execute this stage"""
        if game_state.config.debug:
            print(f"Executing stage: {self.stage_name}")