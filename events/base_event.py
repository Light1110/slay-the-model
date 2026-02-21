"""
Base event definitions for new architecture.
Events use global action queue - they represent random encounters in Unknown Rooms.
"""
from utils.result_types import BaseResult
from engine.game_state import game_state
from localization import Localizable


class Event(Localizable):
    """
    Base event class - represents a random event in Unknown Rooms.
    
    Events are triggered when entering an Unknown Room that resolves
    to an EVENT type. Events can provide rewards, trigger combat,
    or offer choices to the player.
    """
    
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        
        # Control flag for ending event
        self.event_ended = False
    
    def trigger(self) -> 'BaseResult':
        """
        Trigger and execute the event.

        This method should implement the event's main logic,
        building and executing actions as needed.

        Returns:
            BaseResult: The result of this event.
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement trigger()")
    
    def end_event(self) -> None:
        """End the event and return to room flow"""
        self.event_ended = True
    
    def __str__(self):
        return f"{self.__class__.__name__}()"
