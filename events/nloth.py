"""Event: N'loth - Act 2 Shrine Event

Trade a relic for N'loth's Gift (duplicate obtained cards 50% chance).
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddRelicAction, LoseRelicAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from relics.global_relics.event import NlothGift


@register_event(event_id='nloth', acts=[2], weight=100)
class Nloth(Event):
    """N'loth - trade relic for N'loth's Gift."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Only appears if player has 2+ relics."""
        return len(game_state.player.relics) >= 2
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.nloth.description'
        ))
        
        # Build options - offer to trade a relic
        # todo: 修改逻辑
        # option1: 失去随机遗物1，获得NlothGift
        # option2: 失去随机遗物2，获得NlothGift
        # option3: 离开
        options = [
            Option(
                # todo: name 要让玩家知道，即将损失的遗物是哪一个？
                name=LocalStr('events.nloth.offer_relic'),
                actions=[
                    # TODO: 失去指定的遗物
                    LoseRelicAction(relic=game_state.player.relics[0] if game_state.player.relics else None),
                    AddRelicAction(relic=NlothGift())
                ]
            ),
            Option(
                name=LocalStr('events.nloth.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.nloth.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
