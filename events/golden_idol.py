"""Event: Golden Idol - Act 1 Event

A relic event with trap consequences. Taking the idol triggers a trap.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddCardAction
from actions.reward import AddRelicAction
from actions.combat import LoseHPAction, ModifyMaxHpAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import GoldenIdol
from cards.colorless import Injury


@register_event(category='event', event_id='golden_idol', acts=[1], weight=100)
class GoldenIdolEvent(Event):
    """Golden Idol - take relic and face trap consequences."""
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.golden_idol.description'
        ))
        
        # Calculate HP amounts (ModifyMaxHpAction uses amount, not percent)
        smash_percent = 0.35 if game_state.ascension >= 15 else 0.25
        hide_percent = 0.10 if game_state.ascension >= 15 else 0.08
        # Calculate negative amount for losing MaxHP
        hide_hp_loss = -int(game_state.player.max_hp * hide_percent)
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.golden_idol.take'),
                detail=LocalStr('events.golden_idol.take_detail'),
                actions=[
                    AddRelicAction(relic=GoldenIdol()),
                    # Triggers trap - player must choose:
                    InputRequestAction(
                        title=LocalStr('events.golden_idol.trap'),
                        options=[
                            Option(
                                name=LocalStr('events.golden_idol.outrun'),
                                detail=LocalStr('events.golden_idol.outrun_detail'),
                                actions=[AddCardAction(card=Injury())]
                            ),
                            Option(
                                name=LocalStr('events.golden_idol.smash'),
                                detail=LocalStr('events.golden_idol.smash_detail', hp=int(game_state.player.max_hp * smash_percent)),
                                actions=[LoseHPAction(percent=smash_percent)]
                            ),
                            Option(
                                name=LocalStr('events.golden_idol.hide'),
                                detail=LocalStr('events.golden_idol.hide_detail', hp=-hide_hp_loss),
                                actions=[ModifyMaxHpAction(amount=hide_hp_loss)]
                            )
                        ]
                    )
                ]
            ),
            Option(
                name=LocalStr('events.golden_idol.leave'),
                detail=LocalStr('events.no_effect'),
                actions=[]
            )
        ]
        
        actions.append(InputRequestAction(
            title=LocalStr('events.golden_idol.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)
