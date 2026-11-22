"""Event: Sensory Stone - Act 3 Event

Colorless cards for HP trade.
"""
from engine.random_streams import get_rng
from engine.runtime_api import add_action, add_actions

from events.base_event import Event
from events.event_pool import register_event
from actions.base import LambdaAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option


@register_event(category='event', event_id='sensory_stone', acts=[3], weight=100)
class SensoryStone(Event):
    """Sensory Stone - colorless cards for HP."""
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.sensory_stone.description'
        ))
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.sensory_stone.recall_1'),
                detail=LocalStr('events.sensory_stone.recall_1_detail'),
                actions=[
                    LambdaAction(self._show_memory),
                    AddRandomCardAction(namespace='colorless')
                ]
            ),
            Option(
                name=LocalStr('events.sensory_stone.recall_2'),
                detail=LocalStr('events.sensory_stone.recall_2_detail'),
                actions=[
                    LambdaAction(self._show_memory),
                    LoseHPAction(amount=5),
                    AddRandomCardAction(namespace='colorless'),
                    AddRandomCardAction(namespace='colorless')
                ]
            ),
            Option(
                name=LocalStr('events.sensory_stone.recall_3'),
                detail=LocalStr('events.sensory_stone.recall_3_detail'),
                actions=[
                    LambdaAction(self._show_memory),
                    LoseHPAction(amount=10),
                    AddRandomCardAction(namespace='colorless'),
                    AddRandomCardAction(namespace='colorless'),
                    AddRandomCardAction(namespace='colorless')
                ]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.sensory_stone.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)

    def _show_memory(self) -> None:
        memories = [1, 2, 3, 4]
        get_rng("misc").shuffle(memories)
        add_action(DisplayTextAction(text_key=f"events.sensory_stone.memory_{memories[0]}"), to_front=True)
