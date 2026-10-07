"""Event: The Colosseum - Act 2 Event

Double fight for big rewards.
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import StartFightAction
from actions.base import LambdaAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='the_colosseum', acts=[2], weight=100)
class TheColosseum(Event):
    """The Colosseum - double fight for rewards.
    
    [Fight] Fight the Slavers (Blue Slaver + Red Slaver) - NO REWARDS
    After winning the first fight:
    [Victory] Fight Taskmaster + Gremlin Nob -> 100g + rare relic + uncommon relic + card
    [Cowardice] Escape with your life
    [Leave] Always available - Leave the arena
    """
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears on Floor 7+ of Act 2."""
        # Colosseum appears on Floor 7+ of Act 2
        # Note: In original game, this is Floor 7+ regardless of ascension
        return game_state.current_act == 2 and game_state.floor_in_act >= 7
    
    def __init__(self):
        super().__init__()
        self.first_fight_done = False
    
    def _finish_first_fight(self) -> None:
        self.first_fight_done = True
        self.trigger()

    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.the_colosseum.description'
        ))
        
        if not self.first_fight_done:
            from enemies.act1.slaver import BlueSlaver, RedSlaver

            actions.append(StartFightAction(
                enemies=[BlueSlaver(), RedSlaver()],
                victory_actions=[LambdaAction(self._finish_first_fight)],
            ))
        else:
            from enemies.act1.gremlin_nob import GremlinNob
            from enemies.act2.taskmaster import Taskmaster

            actions.append(InputRequestAction(
                title=LocalStr('events.the_colosseum.title'),
                options=[
                    Option(
                        name=LocalStr('events.the_colosseum.victory'),
                        actions=[
                            StartFightAction(
                                enemies=[Taskmaster(), GremlinNob()],
                                victory_actions=[
                                    AddGoldAction(amount=100),
                                    AddRandomRelicAction(rarity='rare'),
                                    AddRandomRelicAction(rarity='uncommon'),
                                    AddRandomCardAction(),
                                    LambdaAction(self.end_event),
                                ],
                            )
                        ],
                    ),
                    Option(
                        name=LocalStr('events.the_colosseum.cowardice'),
                        actions=[LambdaAction(self.end_event)],
                    ),
                ],
            ))
        
        add_actions(actions)
