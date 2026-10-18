"""Event: Mind Bloom - Act 3 Event

Powerful choices with consequences (boss fight, upgrade all, gold, or heal).
"""
from engine.runtime_api import add_action, add_actions, publish_message, request_input, set_terminal_state

from events.base_event import Event
from events.event_pool import register_event
from actions.display import InputRequestAction, DisplayTextAction
from actions.card import AddRandomCardAction, UpgradeCardAction, UpgradeAllCardsAction, AddCardAction
from actions.reward import AddGoldAction, AddRandomRelicAction, AddRelicAction
from actions.combat import HealAction, StartFightAction
from utils.registry import get_registered
from localization import LocalStr
from utils.option import Option
from engine.game_state import game_state
from cards.colorless import Normality, Doubt
from relics.global_relics.event import MarkOfBloom


@register_event(event_id='mind_bloom', acts=[3], weight=100)
class MindBloom(Event):
    """Mind Bloom - powerful choices with consequences."""
    
    @classmethod
    def can_appear(cls) -> bool:
        """Appears on all ascensions in Act 3."""
        return True
    
    def trigger(self) -> None:
        actions = []
        
        # Display event description
        actions.append(DisplayTextAction(
            text_key='events.mind_bloom.description'
        ))
        
        # Gold for "I am War" option (reduced on A15+)
        war_gold = 25 if game_state.ascension >= 15 else 50
        
        # Create random Act 1 boss for "I am War" option
        import random
        act1_bosses = ['hexaghost', 'slaver', 'the_guardian']  # Act 1 bosses
        boss_name = random.choice(act1_bosses)
        boss_class = get_registered("enemy", boss_name)
        boss_enemies = [boss_class()] if boss_class else []
        
        # Build options
        options = [
            Option(
                name=LocalStr('events.mind_bloom.i_am_war'),
                detail=LocalStr('events.mind_bloom.war_detail', gold=war_gold),
                actions=[
                    StartFightAction(
                        enemies=boss_enemies,
                        victory_actions=[
                            AddRandomRelicAction(rarity='rare'),
                            AddGoldAction(amount=war_gold),
                            AddRandomCardAction()
                        ]
                    )
                ]
            ),
            Option(
                name=LocalStr('events.mind_bloom.i_am_awake'),
                detail=LocalStr('events.mind_bloom.awake_detail'),
                actions=[
                    UpgradeAllCardsAction(),
                    AddRelicAction(relic=MarkOfBloom())
                ]
            ),
        ]
        if game_state.current_floor % 50 <= 40:
            options.append(Option(
                name=LocalStr('events.mind_bloom.i_am_rich'),
                detail=LocalStr('events.mind_bloom.rich_detail', gold=999),
                actions=[AddGoldAction(amount=999), AddCardAction(card=Normality()),
                         AddCardAction(card=Normality())],
            ))
        else:
            options.append(Option(
                name=LocalStr('events.mind_bloom.i_am_healthy'),
                detail=LocalStr('events.mind_bloom.healthy_detail'),
                actions=[HealAction(percent=1.0), AddCardAction(card=Doubt())],
            ))

        actions.append(InputRequestAction(
            title=LocalStr('events.mind_bloom.title'),
            options=options
        ))
        
        self.end_event()
        add_actions(actions)
