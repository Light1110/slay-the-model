"""
Miscellaneous actions
"""
from actions.base import Action
from localization import t
from utils.registry import register

@register("action")
class MoveToPositionAction(Action):
    """Move to a new position
    
    Required:
        position (str): Target position
        
    Optional:
        None
    """
    def __init__(self, position: str):
        self.position = position
    
    def execute(self):
        from engine.game_state import game_state
        if self.position:
            game_state.move_to_position(self.position)
        game_state.current_floor += 1

@register("action")
class GenerateMapAction(Action):
    """Generate a new map and update global state
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self):
        from engine.game_state import game_state
        game_state.generate_initial_map()
        print(self.translate("ui.map_generated", default="Map generated for new act!"))

@register("action")
class StartEventAction(Action):
    """Action to start an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.start_event()
            
@register("action")
class EndEventAction(Action):
    """Action to end an event - inserted to queue head
    
    Required:
        None
        
    Optional:
        None
    """
    def __init__(self):
        pass
    
    def execute(self):
        from engine.game_state import game_state
        current_event = game_state.current_event
        if current_event:
            current_event.end_event()