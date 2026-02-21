"""Event: Face Trader - Shrine Event (Act 1-2)

Trade HP for gold or gamble for face relics.
"""

from utils.result_types import BaseResult, MultipleActionsResult
from events.base_event import Event
from events.event_pool import register_event
from actions.display import SelectAction, DisplayTextAction
from actions.reward import AddGoldAction, AddRandomRelicAction
from actions.combat import LoseHPAction
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state


@register_event(event_id='face_trader', acts=[1, 2], weight=100)
class FaceTrader(Event):
    """Face Trader - trade HP for gold or gamble for face relics."""
    
    def trigger(self) -> BaseResult:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.face_trader.description'
        ))
        
        # Calculate HP loss percentage
        hp_percent = 0.15 if game_state.ascension >= 15 else 0.10
        gold_amount = 50 if game_state.ascension >= 15 else 75
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.face_trader.touch'),
                actions=[
                    LoseHPAction(percent=hp_percent),
                    AddGoldAction(amount=gold_amount)
                ]
            ),
            Option(
                name=LocalStr('events.face_trader.trade'),
                actions=[
                    # 50/50 chance for good/bad face relic
                    # todo: 删除 AddRandomRelicAction 中的 pool 字段
                    # 这里应该先随机选一个遗物，然后直接AddRelicAction
                    """
                    ```markdown
# Options ⚜️
Numbers in parentheses are for Ascension 15 or higher.
- [Touch] Lose HP equal to 10% of Max HP. Gain 75 (50) Gold.
- [Trade] Receive one of the following event relics:
  - 🧠 Cultist Headpiece: You feel more talkative (Neutral Face).
  - 🙏 Face of Cleric: Raise your Max HP by 1 after each combat (Good Face).
  - 😈 Gremlin Visage: Start each combat with 1 🦴 Weak (Bad Face).
  - 🤔 N'loth's Hungry Face: The next non-boss Chest you open is empty (Bad Face).
  - 🐍 Ssserpent Head: Whenever you enter a ? room, gain 50 Gold (Good Face).
```

                    """
                    AddRandomRelicAction(pool='face')
                ]
            ),
            Option(
                name=LocalStr('events.face_trader.leave'),
                actions=[]
            )
        ]
        
        actions.append(SelectAction(
            title=LocalStr('events.face_trader.title'),
            options=options
        ))
        
        self.end_event()
        return MultipleActionsResult(actions)
