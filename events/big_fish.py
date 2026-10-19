"""
Event 1 - Big Fish
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state
from events.base_event import Event
from actions.base import LambdaAction
from actions.card import AddCardAction
from actions.combat import HealAction, ModifyMaxHpAction
from actions.display import InputRequestAction, DisplayTextAction
from actions.reward import AddRandomRelicAction
from events.event_pool import register_event
from localization import LocalStr
from utils.option import Option
from utils.types import RarityType
from cards.colorless.regret import Regret


@register_event(
    category="event",
    event_id="big_fish",
    acts=[1],
    weight=100
)
class BigFishEvent(Event):
    """
    Big Fish Event
    
    [Banana] Heal 1/3 of your max HP (rounded down)
    [Donut] Max HP +5 (extra HP is healed when obtained)
    [Box] Receive a random Relic (Common/Uncommon/Rare). Become Cursed: Regret
    """
    
    def trigger(self) -> None:
        """Trigger big fish blessing event"""
        from engine.game_state import game_state
        
        # Collect all actions
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key="events.big_fish.description"
        ))
        
        heal_amount = game_state.player.max_hp // 3

        # Build options
        options = []
        
        # Option 1: Banana - Heal 1/3 of max HP (rounded down)
        options.append(Option(
            name=LocalStr("events.big_fish.option1"),
            detail=LocalStr('events.big_fish.banana_detail', heal=heal_amount),
            actions=[
                HealAction(amount=heal_amount),
                LambdaAction(lambda: self.end_event()),
            ]
        ))
        
        # Option 2: Donut - Max HP +5
        options.append(Option(
            name=LocalStr("events.big_fish.option2"),
            detail=LocalStr('events.big_fish.donut_detail', hp=5),
            actions=[
                ModifyMaxHpAction(amount=5),  # Positive = gain Max HP
                LambdaAction(lambda: self.end_event()),
            ]
        ))
        
        # Option 3: Box - Receive a random relic + Regret curse
        options.append(Option(
            name=LocalStr("events.big_fish.option3"),
            detail=LocalStr('events.big_fish.box_detail'),
            actions=[
                AddRandomRelicAction(
                    rarities=[RarityType.COMMON, RarityType.UNCOMMON, RarityType.RARE]
                ),
                AddCardAction(card=Regret()),
                LambdaAction(lambda: self.end_event()),
            ]
        ))
        
        # Display options and wait for selection
        actions.append(InputRequestAction(
            title=LocalStr("events.big_fish.title"),
            options=options
        ))
        
        add_actions(actions)
