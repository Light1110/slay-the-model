"""
Event room definitions.

Event rooms are rooms where random events occur when player enters.
Events can offer choices, rewards, or challenges based on game state.
"""
from typing import List

from actions.base import LambdaAction
from actions.display import DisplayTextAction, SelectAction
from localization import LocalStr
from rooms.base import Room
from utils.result_types import BaseResult, NoneResult, GameStateResult, MultipleActionsResult, SingleActionResult
from utils.types import RoomType
from utils.random import get_random_events
from utils.option import Option
from utils.registry import register

@register("room")
class EventRoom(Room):
    """
    Event room - presents random events to the player.
    
    When the player enters an event room, they are presented with one or more
    random events based on game state (floor, act, ascension, etc.).
    The player can then choose which event to engage with.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize event room.
        
        Args:
            **kwargs: Additional room parameters
        """
        super().__init__(**kwargs)
        self.room_type = RoomType.EVENT
        
        # List of available events for this room
        self.available_events: List = []
        
        # The event that was selected and triggered
        self.triggered_event = None
    
    def init(self):
        """
        Initialize event room and generate available events.
        
        Generates a list of available events based on current game state
        including Act number and ascension level.
        """
        from engine.game_state import game_state
        import events  # Ensure all @register_event decorators are loaded.
        
        # Get random events based on current Act
        event_count = self._get_event_count(game_state.current_act)
        
        # Get events from pool
        self.available_events = get_random_events(
            act=game_state.current_act,
            count=event_count
        )
        
        # If no events available, create a fallback event
        if not self.available_events:
            self._create_fallback_event()
    
    def enter(self) -> BaseResult:
        """
        Enter event room and directly trigger a random event.

        Returns:
            Execution result from event or NoneResult
        """
        # Display room description
        display_action = DisplayTextAction(
            text_key="rooms.event.enter",
            default="You encounter a mysterious event...",
        )

        # Check if we have available events
        if not self.available_events:
            # No events available, just return the display action
            return SingleActionResult(display_action)

        # Multiple events: let player choose one event to engage with.
        if len(self.available_events) > 1:
            options = []
            for event in self.available_events:
                options.append(
                    Option(
                        name=self._get_event_option_name(event),
                        actions=[LambdaAction(func=self._trigger_event, args=[event])],
                    )
                )
            return MultipleActionsResult(
                [
                    display_action,
                    SelectAction(
                        title=LocalStr(
                            "rooms.event.choose",
                            default="Choose an event",
                        ),
                        options=options,
                    ),
                ]
            )

        # Single event: trigger directly.
        event_result = self._trigger_event(self.available_events[0])
        return self._merge_display_with_result(display_action, event_result)
    
    def _get_event_count(self, act: int) -> int:
        """
        Determine how many events to offer based on Act.
        
        Args:
            act: Current Act number (1-3)
            
        Returns:
            Number of events to present
        """
        # Act 1: offer 1 event
        if act == 1:
            return 1
        # Act 2: offer 2 events
        elif act == 2:
            return 2
        # Act 3+: offer up to 3 events
        else:
            return 3
    
    def _trigger_event(self, event) -> BaseResult:
        """
        Trigger a specific event.
        
        Args:
            event: The event instance to trigger
            
        Returns:
            Result from event trigger
        """
        # Mark the triggered event
        self.triggered_event = event
        
        # Execute event's trigger method
        if hasattr(event, 'trigger'):
            result = event.trigger()
            
            # Mark room as ready to leave after event completes
            self.should_leave = True
            
            return result

        return NoneResult()
    
    def _create_fallback_event(self):
        """
        Create a fallback event when no events are available.

        This ensures that room always has something to offer.
        """
        # Create a simple fallback event that just gives some gold
        from events.base_event import Event
        from utils.result_types import SingleActionResult

        class FallbackEvent(Event):
            def trigger(self):
                from engine.game_state import game_state
                from localization import t
                from actions.display import DisplayTextAction

                gold_gain = 10 + (game_state.current_floor * 5)
                game_state.player.gold += gold_gain

                return SingleActionResult(
                    DisplayTextAction(
                        text_key="rooms.event.fallback",
                        default=f"You found {gold_gain} gold!",
                    )
                )

        self.available_events = [FallbackEvent()]

    def _get_event_option_name(self, event) -> LocalStr:
        """Build display text for an event option."""
        if hasattr(event, "local"):
            try:
                return event.local("title")
            except Exception:
                pass
        return LocalStr(
            key=f"events.{event.__class__.__name__}.title",
            default=event.__class__.__name__,
        )

    def _merge_display_with_result(
        self, display_action: DisplayTextAction, event_result: BaseResult
    ) -> BaseResult:
        """Attach room entry display to event execution result."""
        if isinstance(event_result, GameStateResult):
            return event_result
        if isinstance(event_result, SingleActionResult):
            return MultipleActionsResult([display_action, event_result.action])
        if isinstance(event_result, MultipleActionsResult):
            return MultipleActionsResult([display_action] + event_result.actions)
        return SingleActionResult(display_action)
